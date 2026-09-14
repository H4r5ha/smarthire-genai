# src/search/embed.py
from __future__ import annotations

import importlib
import re
import time
from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import numpy as np

from .. import config
from ..core.paths import EMBEDDING_MODEL_DIR


class EmbeddingError(RuntimeError):
    """Raised when the configured embedding backend cannot run."""


@dataclass
class _LSAEmbedder:
    vectorizer: object
    reducer: object | None

    def encode(self, texts: list[str]) -> np.ndarray:
        matrix = self.vectorizer.transform(texts)

        if self.reducer is not None:
            matrix = self.reducer.transform(matrix)

        arr = np.asarray(matrix, dtype="float32")
        norms = np.linalg.norm(arr, axis=1, keepdims=True)

        return arr / np.clip(norms, 1e-12, None)


_embedder: _LSAEmbedder | None = None
_gemini_client = None


def _ensure_dir() -> None:
    EMBEDDING_MODEL_DIR.mkdir(parents=True, exist_ok=True)


def _load_lsa() -> _LSAEmbedder:
    global _embedder

    if _embedder is not None:
        return _embedder

    try:
        import joblib
    except Exception as exc:
        raise EmbeddingError(
            "scikit-learn/joblib is required for the lightweight embedding backend."
        ) from exc

    vectorizer_path = EMBEDDING_MODEL_DIR / "tfidf_vectorizer.joblib"
    reducer_path = EMBEDDING_MODEL_DIR / "lsa_reducer.joblib"

    if not vectorizer_path.exists():
        raise EmbeddingError(
            "Embedding model is not built yet. "
            "Run `python scripts\\build_index.py` first."
        )

    vectorizer = joblib.load(vectorizer_path)
    reducer = joblib.load(reducer_path) if reducer_path.exists() else None

    _embedder = _LSAEmbedder(
        vectorizer=vectorizer,
        reducer=reducer,
    )

    return _embedder


def _fit_lsa(texts: list[str]) -> _LSAEmbedder:
    """Build a compact local semantic representation without downloading a neural model.

    TF-IDF + truncated SVD (LSA) is retained as the offline fallback.
    It is deterministic, CPU-only, requires no model download, and is suitable
    for low-memory Windows development environments.
    """
    try:
        import joblib
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
    except Exception as exc:
        raise EmbeddingError(
            "Install the project requirements before building the index."
        ) from exc

    if not texts:
        raise EmbeddingError("No job documents were found to embed.")

    # Keep vocabulary intentionally bounded for low-memory machines.
    vectorizer = TfidfVectorizer(
        strip_accents="unicode",
        lowercase=True,
        ngram_range=(1, 2),
        max_features=config.EMBEDDING_MAX_FEATURES,
        min_df=1,
        sublinear_tf=True,
    )

    sparse = vectorizer.fit_transform(texts)

    # For small corpora the number of SVD components must be below the matrix rank.
    max_components = max(
        1,
        min(
            config.EMBEDDING_DIMENSION,
            sparse.shape[0] - 1,
            sparse.shape[1] - 1,
        ),
    )

    reducer = None

    if max_components >= 2:
        reducer = TruncatedSVD(
            n_components=max_components,
            random_state=42,
            n_iter=3,
        )
        reducer.fit(sparse)

    _ensure_dir()

    joblib.dump(
        vectorizer,
        EMBEDDING_MODEL_DIR / "tfidf_vectorizer.joblib",
        compress=3,
    )

    if reducer is not None:
        joblib.dump(
            reducer,
            EMBEDDING_MODEL_DIR / "lsa_reducer.joblib",
            compress=3,
        )
    else:
        old = EMBEDDING_MODEL_DIR / "lsa_reducer.joblib"

        if old.exists():
            old.unlink()

    _embedder = _LSAEmbedder(
        vectorizer=vectorizer,
        reducer=reducer,
    )

    return _embedder


def _normalise_vectors(vectors: np.ndarray) -> np.ndarray:
    vectors = np.asarray(vectors, dtype="float32")

    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)

    return vectors / np.clip(norms, 1e-12, None)


# ------------------------------------------------------------
# Free-tier rate limiting for embed_content.
# The free tier caps embedding requests at ~100/minute; without this,
# a 500-row job corpus fires enough requests to trigger 429s immediately.
# ------------------------------------------------------------
# Google counts each TEXT inside a batch against the per-minute quota,
# not each API call - a single 64-item batch call already uses 64/100 of
# the budget. The limiter below tracks weighted usage (items, not calls).
_GEMINI_EMBED_MAX_ITEMS_PER_MINUTE = 90  # safety margin under the 100 cap
_GEMINI_EMBED_MAX_RETRIES = 6
_request_log: deque[tuple[float, int]] = deque()  # (timestamp, item_count)


def _rate_limit_wait(item_count: int) -> None:
    """Block until sending item_count more items keeps us under the per-minute cap."""
    window_seconds = 60.0
    now = time.monotonic()

    while _request_log and now - _request_log[0][0] > window_seconds:
        _request_log.popleft()

    used = sum(count for _, count in _request_log)

    if used + item_count > _GEMINI_EMBED_MAX_ITEMS_PER_MINUTE:
        oldest_time = _request_log[0][0] if _request_log else now
        sleep_for = window_seconds - (now - oldest_time) + 0.5

        if sleep_for > 0:
            print(
                f"[embed] Pacing for free-tier rate limit, "
                f"pausing {sleep_for:.1f}s before next batch of {item_count}..."
            )
            time.sleep(sleep_for)

        now = time.monotonic()

        while _request_log and now - _request_log[0][0] > window_seconds:
            _request_log.popleft()

    _request_log.append((time.monotonic(), item_count))


def _is_daily_quota_exhausted(exc: Exception) -> bool:
    """True for Google's *daily* free-tier quota (resets in ~24h), as opposed
    to an ordinary per-minute rate limit that a short retry can ride out.
    Retrying a per-day quota error with a 20-60s backoff is pointless and just
    makes the user wait several minutes for a failure that was certain from
    the first attempt."""
    text = str(exc)
    return "RESOURCE_EXHAUSTED" in text and "PerDay" in text


def _parse_retry_delay(exc: Exception, default: float = 20.0) -> float:
    """Pull Google's suggested 'retry in Xs' delay out of the error, if present."""
    match = re.search(r"retry in ([0-9.]+)s", str(exc))

    if match:
        try:
            return float(match.group(1)) + 1.0
        except ValueError:
            pass

    return default


def _get_gemini_client():
    global _gemini_client

    if _gemini_client is not None:
        return _gemini_client

    if not config.GEMINI_API_KEY:
        raise EmbeddingError(
            "GEMINI_API_KEY is not configured."
        )

    try:
        from google import genai
    except Exception as exc:
        raise EmbeddingError(
            "The google-genai package is required for Gemini embeddings."
        ) from exc

    try:
        _gemini_client = genai.Client(
            api_key=config.GEMINI_API_KEY
        )
        return _gemini_client
    except Exception as exc:
        raise EmbeddingError(
            f"Could not initialise the Gemini embedding client: {exc}"
        ) from exc


def _embed_gemini_batch(texts: list[str]) -> np.ndarray:
    """Embed one batch of texts using the Gemini embeddings API."""
    if not texts:
        raise EmbeddingError("Cannot embed an empty Gemini batch.")

    client = _get_gemini_client()

    from google.genai import types

    contents = [
        types.Content(
            parts=[
                types.Part.from_text(text=text)
            ]
        )
        for text in texts
    ]

    result = None
    last_exc: Exception | None = None

    for attempt in range(1, _GEMINI_EMBED_MAX_RETRIES + 1):
        _rate_limit_wait(len(texts))

        try:
            result = client.models.embed_content(
                model=config.GEMINI_EMBEDDING_MODEL,
                contents=contents,
                config=types.EmbedContentConfig(
                    output_dimensionality=config.GEMINI_EMBEDDING_DIMENSION,
                ),
            )
            break

        except Exception as exc:
            last_exc = exc

            if _is_daily_quota_exhausted(exc):
                # A per-day quota will not recover within this request no
                # matter how long we wait, so fail immediately with a clear,
                # actionable message instead of retrying for several minutes.
                raise EmbeddingError(
                    "Your Gemini free-tier daily embedding quota has been used up for today "
                    "(embed_content, limit 1000 requests/day). This resets on its own in "
                    "roughly 24 hours, or you can enable billing on this API key's Google AI "
                    "Studio project to lift the limit sooner. See "
                    "https://ai.google.dev/gemini-api/docs/rate-limits for details. "
                    "This is a quota limit, not a bug in the app."
                ) from exc

            is_rate_limit = (
                "429" in str(exc)
                or "RESOURCE_EXHAUSTED" in str(exc)
            )

            if is_rate_limit and attempt < _GEMINI_EMBED_MAX_RETRIES:
                delay = _parse_retry_delay(exc)

                print(
                    f"[embed] Rate limited (attempt {attempt}/"
                    f"{_GEMINI_EMBED_MAX_RETRIES}), waiting {delay:.1f}s..."
                )

                time.sleep(delay)
                continue

            raise EmbeddingError(
                f"Gemini embedding request failed: {exc}"
            ) from exc

    if result is None:
        raise EmbeddingError(
            f"Gemini embedding request failed after retries: {last_exc}"
        ) from last_exc

    embeddings = getattr(result, "embeddings", None)

    if not embeddings:
        raise EmbeddingError(
            "Gemini returned no embeddings."
        )

    try:
        vectors = np.asarray(
            [embedding.values for embedding in embeddings],
            dtype="float32",
        )
    except Exception as exc:
        raise EmbeddingError(
            f"Gemini returned an unexpected embedding response: {exc}"
        ) from exc

    if len(vectors) != len(texts):
        raise EmbeddingError(
            "Gemini returned a different number of embeddings than inputs."
        )

    return _normalise_vectors(vectors)


def _embed_gemini(texts: list[str]) -> np.ndarray:
    """Embed texts through Gemini in bounded batches."""
    if not texts:
        return np.empty(
            (0, config.GEMINI_EMBEDDING_DIMENSION),
            dtype="float32",
        )

    vectors: list[np.ndarray] = []

    for start in range(0, len(texts), config.EMBEDDING_BATCH_SIZE):
        batch = texts[start:start + config.EMBEDDING_BATCH_SIZE]
        vectors.append(_embed_gemini_batch(batch))

    return np.vstack(vectors).astype("float32")


# ------------------------------------------------------------
# FastEmbed local model cache
# ------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_fastembed_model():
    """Load the FastEmbed model once and reuse it."""
    try:
        fastembed_module = importlib.import_module("fastembed")
        TextEmbedding = fastembed_module.TextEmbedding
    except Exception as exc:
        raise EmbeddingError(
            "FastEmbed is not installed. "
            "Use EMBEDDING_PROVIDER=gemini-api or local-lsa."
        ) from exc

    try:
        return TextEmbedding(
            model_name=config.LOCAL_EMBEDDING_MODEL,
            threads=1,
        )
    except Exception as exc:
        raise EmbeddingError(
            f"FastEmbed model initialisation failed: {exc}"
        ) from exc


def _embed_fastembed(texts: list[str]) -> np.ndarray:
    """Embed texts using the cached FastEmbed model.

    The TextEmbedding model itself is loaded only once through
    _get_fastembed_model(). The actual embedding computation remains
    fresh for every call and input batch.
    """
    try:
        model = _get_fastembed_model()

        vectors = np.asarray(
            list(
                model.embed(
                    texts,
                    batch_size=config.EMBEDDING_BATCH_SIZE,
                )
            ),
            dtype="float32",
        )

        return _normalise_vectors(vectors)

    except EmbeddingError:
        raise
    except Exception as exc:
        raise EmbeddingError(
            f"FastEmbed failed: {exc}"
        ) from exc


def fit_and_embed_texts(
    texts: Iterable[str],
) -> tuple[np.ndarray, dict]:
    """Create vectors for an index using the configured embedding provider."""
    values = [str(t or "") for t in texts]

    if not values:
        raise EmbeddingError(
            "No job documents were found to embed."
        )

    provider = config.EMBEDDING_PROVIDER

    # ------------------------------------------------------------
    # Gemini API: PRIMARY / DEFAULT PROVIDER
    # ------------------------------------------------------------
    if provider in {"gemini-api", "gemini"}:
        if not config.GEMINI_API_KEY:
            raise EmbeddingError(
                "GEMINI_API_KEY is not configured. "
                "Set the Gemini API key before building a Gemini embedding index."
            )

        vectors = _embed_gemini(values)

        return vectors, {
            "provider": "gemini-api",
            "model": config.GEMINI_EMBEDDING_MODEL,
            "dimension": int(vectors.shape[1]),
            "batch_size": config.EMBEDDING_BATCH_SIZE,
        }

    # ------------------------------------------------------------
    # Local LSA: OFFLINE FALLBACK
    # ------------------------------------------------------------
    if provider in {"local", "local-lsa", "lsa", "tfidf"}:
        embedder = _fit_lsa(values)
        vectors = embedder.encode(values)

        return vectors, {
            "provider": "local-lsa",
            "model": "TF-IDF + TruncatedSVD",
            "dimension": int(vectors.shape[1]),
            "max_features": config.EMBEDDING_MAX_FEATURES,
        }

    # ------------------------------------------------------------
    # FastEmbed: OPTIONAL LOCAL NEURAL PROVIDER
    # ------------------------------------------------------------
    if provider == "fastembed":
        vectors = _embed_fastembed(values)

        return vectors, {
            "provider": "fastembed",
            "model": config.LOCAL_EMBEDDING_MODEL,
            "dimension": int(vectors.shape[1]),
            "batch_size": config.EMBEDDING_BATCH_SIZE,
        }

    raise EmbeddingError(
        f"Unsupported EMBEDDING_PROVIDER={provider!r}. "
        "Use gemini-api, local-lsa, or fastembed."
    )


def embed_texts(texts: Iterable[str]) -> np.ndarray:
    """Embed query texts using the same provider as the stored index."""
    values = [str(t or "") for t in texts]

    if not values:
        provider = config.EMBEDDING_PROVIDER

        if provider in {"gemini-api", "gemini"}:
            dimension = config.GEMINI_EMBEDDING_DIMENSION
        elif provider == "fastembed":
            dimension = config.EMBEDDING_DIMENSION
        else:
            dimension = config.EMBEDDING_DIMENSION

        return np.empty(
            (0, dimension),
            dtype="float32",
        )

    provider = config.EMBEDDING_PROVIDER

    # ------------------------------------------------------------
    # Gemini API
    # IMPORTANT: no silent LSA fallback.
    # The query must remain in the same embedding space as the index.
    # ------------------------------------------------------------
    if provider in {"gemini-api", "gemini"}:
        if not config.GEMINI_API_KEY:
            raise EmbeddingError(
                "GEMINI_API_KEY is not configured. "
                "A Gemini embedding index cannot be queried without the API key."
            )

        return _embed_gemini(values)

    # ------------------------------------------------------------
    # Local LSA
    # ------------------------------------------------------------
    if provider in {"local", "local-lsa", "lsa", "tfidf"}:
        return _load_lsa().encode(values)

    # ------------------------------------------------------------
    # FastEmbed
    # ------------------------------------------------------------
    if provider == "fastembed":
        return _embed_fastembed(values)

    raise EmbeddingError(
        f"Unsupported EMBEDDING_PROVIDER={provider!r}. "
        "Use gemini-api, local-lsa, or fastembed."
    )