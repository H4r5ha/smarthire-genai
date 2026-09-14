# src/config.py: 
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _setting(name: str, default: str = '') -> str:
    value = os.getenv(name)
    if value is not None and value != '':
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, default))
    except Exception:
        return default


APP_NAME = 'SmartHire GenAI'
GEMINI_API_KEY = _setting('GEMINI_API_KEY').strip()
GEMINI_MODEL = _setting('GEMINI_MODEL', 'gemini-3.8-flash').strip()

# Current stable fallback models used when the selected model returns a temporary
# availability/high-demand error. Override with a comma-separated list if desired.
GEMINI_FALLBACK_MODELS = [
    x.strip() for x in _setting(
        'GEMINI_FALLBACK_MODELS', 'gemini-3.7-flash,gemini-3.6-flash'
    ).split(',') if x.strip()
]
GEMINI_MAX_RETRIES = int(_setting('GEMINI_MAX_RETRIES', '2'))
GEMINI_RETRY_BASE_SECONDS = float(_setting('GEMINI_RETRY_BASE_SECONDS', '1.5'))

# Fixed decoding seed for structured JSON extraction (resume parsing). Paired
# with temperature=0 in gemini_client.generate_json[_from_images] so that
# re-uploading the identical resume/screenshot always extracts the same
# skills/target_role, instead of silently drifting between calls and
# changing the downstream Suggested Roles / job-match results.
GEMINI_SEED = int(_setting('GEMINI_SEED', '7'))
# Primary embedding backend: cloud Gemini embeddings.
# The API-based backend keeps neural model memory off the Streamlit container.
EMBEDDING_PROVIDER = _setting('EMBEDDING_PROVIDER', 'gemini-api').strip().lower()

# Dedicated Gemini embedding model. This is separate from GEMINI_MODEL,
# which is used for text generation.
GEMINI_EMBEDDING_MODEL = _setting(
    'GEMINI_EMBEDDING_MODEL',
    'gemini-embedding-2',
).strip()

# Gemini embedding output size. 768 keeps the deployed index compact.
GEMINI_EMBEDDING_DIMENSION = int(
    _setting('GEMINI_EMBEDDING_DIMENSION', '768')
)

# Keep API requests memory-bounded and avoid excessive request fan-out.
EMBEDDING_BATCH_SIZE = int(
    _setting('EMBEDDING_BATCH_SIZE', '64')
)

# Optional local neural backend.
# Local, heavier — intended for local notebook comparisons, use with caution if deployed.
LOCAL_EMBEDDING_MODEL = _setting(
    'LOCAL_EMBEDDING_MODEL',
    'BAAI/bge-small-en-v1.5',
).strip()

# Existing local-LSA fallback configuration.
EMBEDDING_MAX_FEATURES = int(
    _setting('EMBEDDING_MAX_FEATURES', '4096')
)
EMBEDDING_DIMENSION = int(
    _setting('EMBEDDING_DIMENSION', '128')
)
TOP_K_JOBS = int(_setting('TOP_K_JOBS', '5'))
TOP_K_MENTOR = int(_setting('TOP_K_MENTOR', '5'))
MAX_RESUME_CHARS = int(_setting('MAX_RESUME_CHARS', '30000'))
MENTOR_MIN_SCORE = float(_setting('MENTOR_MIN_SCORE', '0.28'))
JOB_MIN_SCORE = float(_setting('JOB_MIN_SCORE', '0.10'))


def require_gemini() -> None:
    if not GEMINI_API_KEY:
        raise RuntimeError('GEMINI_API_KEY is not configured. Copy .env.example to .env and add your key.')
