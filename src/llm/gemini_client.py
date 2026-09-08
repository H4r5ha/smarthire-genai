from __future__ import annotations

import json
import time
from functools import lru_cache
from typing import Callable, TypeVar

from google import genai
from google.genai import types

from .. import config

T = TypeVar("T")


@lru_cache(maxsize=1)
def client() -> genai.Client:
    config.require_gemini()
    return genai.Client(api_key=config.GEMINI_API_KEY)


def _status_code(exc: Exception) -> int | None:
    for attr in ("code", "status_code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    text = str(exc)
    for code in (429, 500, 502, 503, 504):
        if str(code) in text:
            return code
    return None


def _temporary_api_error(exc: Exception) -> bool:
    code = _status_code(exc)
    if code in {429, 500, 502, 503, 504}:
        return True
    text = str(exc).upper()
    return any(token in text for token in (
        "UNAVAILABLE",
        "RESOURCE_EXHAUSTED",
        "HIGH DEMAND",
        "TEMPORARILY UNAVAILABLE",
        "RATE LIMIT",
    ))


def _model_candidates() -> list[str]:
    seen: set[str] = set()
    models: list[str] = []
    for model in [config.GEMINI_MODEL, *config.GEMINI_FALLBACK_MODELS]:
        model = model.strip()
        if model and model not in seen:
            seen.add(model)
            models.append(model)
    return models


def _friendly_failure(last_exc: Exception | None) -> RuntimeError:
    if last_exc is None:
        return RuntimeError("Gemini did not return a response. Please try again.")
    code = _status_code(last_exc)
    if code in {429, 500, 502, 503, 504} or _temporary_api_error(last_exc):
        return RuntimeError(
            "The AI service is temporarily busy or unavailable. "
            "SmartHire tried the configured Gemini fallback models as well. "
            "Please wait a few seconds and try again."
        )
    return RuntimeError(f"Gemini request failed: {last_exc}")


def _call_with_fallback(build_config: Callable[[], types.GenerateContentConfig], *, prompt: str) -> str:
    last_exc: Exception | None = None

    for model in _model_candidates():
        for attempt in range(max(1, config.GEMINI_MAX_RETRIES)):
            try:
                response = client().models.generate_content(
                    model=model,
                    contents=prompt,
                    config=build_config(),
                )
                text = (response.text or "").strip()
                if text:
                    return text
                raise RuntimeError(f"Gemini model {model} returned an empty response.")
            except Exception as exc:
                last_exc = exc
                if not _temporary_api_error(exc):
                    # Request/configuration errors are not fixed by waiting. Try the
                    # next configured model only for model/service availability errors.
                    break
                if attempt + 1 < max(1, config.GEMINI_MAX_RETRIES):
                    time.sleep(config.GEMINI_RETRY_BASE_SECONDS * (2 ** attempt))
        # Move to the next model after exhausting retries for this model.

    raise _friendly_failure(last_exc) from last_exc


def generate_json(prompt: str, schema: dict) -> dict:
    def build_config() -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=schema,
        )

    text = _call_with_fallback(build_config, prompt=prompt)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini returned invalid structured JSON. Please try again.") from exc


def generate_text(
    prompt: str,
    *,
    max_output_tokens: int = 1200,
) -> str:
    def build_config() -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            thinking_config=types.ThinkingConfig(
                thinking_level="low",
            ),
        )

    return _call_with_fallback(build_config, prompt=prompt)