from __future__ import annotations

import tempfile
from pathlib import Path

from .. import config
from ..generate.prompts import RESUME_PARSE_PROMPT, RESUME_PARSE_SCHEMA
from ..llm.gemini_client import generate_json
from ..safety.guardrails import check_input
from .loader import extract_text


def _normalise(profile: dict) -> dict:
    skills = []
    for s in profile.get('skills', []):
        value = ' '.join(str(s).split()).strip()
        if value and value.lower() not in {x.lower() for x in skills}:
            skills.append(value)
    profile['skills'] = skills[:50]
    profile['certifications'] = profile.get('certifications') or []
    profile['achievements'] = profile.get('achievements') or []
    profile['experience_years'] = max(
        0.0,
        float(profile.get('experience_years', 0) or 0),
    )
    profile['initial'] = (profile.get('name') or 'C')[0].upper()
    fields = [
        profile.get('name'),
        profile.get('email'),
        profile.get('location'),
        profile.get('target_role'),
        profile.get('education'),
        profile.get('summary'),
    ]
    checks = [
        ('Name', bool(fields[0])),
        ('Contact', bool(fields[1] or fields[2])),
        ('Target role', bool(fields[3])),
        ('Skills', bool(skills)),
        ('Experience', bool(profile.get('experience'))),
        ('Education', bool(profile.get('education_items'))),
    ]
    profile['completeness_items'] = checks
    profile['completeness'] = round(
        sum(ok for _, ok in checks) / len(checks) * 100
    )
    return profile


def parse_resume(file_obj) -> dict:
    suffix = Path(file_obj.name).suffix.lower()
    if suffix not in {'.pdf', '.docx', '.txt'}:
        raise ValueError('Unsupported resume format. Use PDF, DOCX or TXT.')

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_obj.getbuffer())
        tmp_path = Path(tmp.name)

    try:
        text = extract_text(tmp_path).strip()
    finally:
        tmp_path.unlink(missing_ok=True)

    if not text:
        raise ValueError('The uploaded document contains no extractable text.')

    text = text[:config.MAX_RESUME_CHARS]

    allowed, message = check_input(text, scope='resume')
    if not allowed:
        raise ValueError(f'Resume could not be processed: {message}')

    profile = generate_json(
        RESUME_PARSE_PROMPT.format(resume_text=text),
        RESUME_PARSE_SCHEMA,
    )

    profile['source'] = 'live'
    return _normalise(profile)