from __future__ import annotations

from .. import config
from ..llm.gemini_client import generate_json
from ..safety.guardrails import check_input
from .prompts import JOB_TITLE_EXTRACT_PROMPT, JOB_TITLE_SCHEMA

# Placeholder-ish strings the model (or a bad fallback) could still hand back.
# If the extracted title collapses to one of these, treat it as "no usable
# title" and fall back to the safety-net heuristic instead of showing it.
_PLACEHOLDER_TITLES = {
    '', 'job opening', 'job description', 'untitled', 'position available',
    'job title', 'role', 'pasted job description', 'n/a', 'not specified',
}


def _fallback_title(jd_text: str) -> str:
    """Best-effort title when the LLM call can't be used or returns nothing
    usable. Mirrors the previous "first non-empty line" behaviour so the UI
    still shows *something* rather than failing the whole paste-a-JD flow."""
    first_line = next(
        (line.strip() for line in jd_text.splitlines() if line.strip()),
        'Pasted Job Description',
    )
    return first_line[:80]


def extract_job_title(jd_text: str) -> str:
    """Return a short job-title/role name for a pasted job description.

    Uses the LLM to read the *whole* pasted text for an explicit title
    (previously only the first line was ever looked at, so a JD that opened
    with a company name or location before stating the role never showed the
    role at all). When no explicit title is present anywhere in the text, the
    model infers a standard, appropriate title from the described skills and
    responsibilities instead of leaving the "Target Job" card mislabeled.

    Falls back to the first non-empty line of the text if the LLM call fails
    or clearly returns nothing usable, so this can never raise and block the
    "paste a JD" flow.
    """
    text = (jd_text or '').strip()
    if not text:
        return 'Pasted Job Description'

    text = text[:config.MAX_RESUME_CHARS]

    try:
        allowed, _message = check_input(text, scope='career')
        if not allowed:
            return _fallback_title(text)

        result = generate_json(
            JOB_TITLE_EXTRACT_PROMPT.format(jd_text=text),
            JOB_TITLE_SCHEMA,
        )
        title = str((result or {}).get('title', '') or '').strip()
        title = ' '.join(title.split())  # collapse stray whitespace/newlines
        if not title or title.strip().casefold() in _PLACEHOLDER_TITLES:
            return _fallback_title(text)
        return title[:80]
    except Exception:
        # Any LLM/network hiccup should not block pasting a JD and moving on
        # to CV Improvement -- just degrade to the old heuristic.
        return _fallback_title(text)
