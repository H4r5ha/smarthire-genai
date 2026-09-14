from __future__ import annotations

import tempfile
from pathlib import Path

from .. import config
from ..generate.prompts import (
    RESUME_PARSE_IMAGE_PROMPT,
    RESUME_PARSE_PROMPT,
    RESUME_PARSE_SCHEMA,
)
from ..llm.gemini_client import generate_json, generate_json_from_images
from ..safety.guardrails import check_input
from .loader import extract_text

# Screenshot upload path: lets a candidate share only the non-identifying part of
# their resume (skills/experience/education) instead of the full file.
IMAGE_SUFFIX_MIME = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_RESUME_IMAGES = 4


def _sanitize_items(items, field_defaults: dict) -> list[dict]:
    """Keep only well-formed dict entries and backfill any sub-field the model
    left out, so downstream rendering never has to assume a key exists.
    Screenshots in particular can legitimately show a partial entry (e.g. an
    experience bullet cut off mid-way), so this must not raise on that."""
    cleaned = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        entry = {}
        for key, default in field_defaults.items():
            value = item.get(key, default)
            if isinstance(default, list):
                entry[key] = [str(v).strip() for v in (value or []) if str(v).strip()]
            else:
                entry[key] = str(value).strip() if value else default
        cleaned.append(entry)
    return cleaned


def _normalise(profile: dict) -> dict:
    if not isinstance(profile, dict):
        profile = {}

    # Scalar text fields: the schema marks these required, but a cropped
    # screenshot can genuinely show no evidence for one (e.g. no email
    # visible), and multimodal responses are more likely than text ones to
    # simply omit a field in that case rather than return an empty string.
    # Default every one defensively instead of trusting it to exist.
    for key in ('name', 'email', 'location', 'target_role', 'education', 'summary'):
        value = profile.get(key)
        profile[key] = value.strip() if isinstance(value, str) else (str(value) if value else '')

    skills = []
    for s in profile.get('skills') or []:
        value = ' '.join(str(s).split()).strip()
        if value and value.lower() not in {x.lower() for x in skills}:
            skills.append(value)
    profile['skills'] = skills[:50]

    profile['experience'] = _sanitize_items(
        profile.get('experience'),
        {'title': '', 'company': '', 'period': '', 'points': []},
    )
    profile['education_items'] = _sanitize_items(
        profile.get('education_items'),
        {'degree': '', 'school': '', 'period': '', 'detail': ''},
    )
    profile['projects'] = _sanitize_items(
        profile.get('projects'),
        {'name': '', 'description': '', 'tech': []},
    )
    profile['certifications'] = _sanitize_items(
        profile.get('certifications'),
        {'name': '', 'issuer': '', 'year': ''},
    )
    profile['achievements'] = [
        str(a).strip() for a in (profile.get('achievements') or []) if str(a).strip()
    ]

    try:
        profile['experience_years'] = max(0.0, float(profile.get('experience_years', 0) or 0))
    except (TypeError, ValueError):
        profile['experience_years'] = 0.0

    profile['initial'] = (profile.get('name') or 'C')[0].upper()

    checks = [
        ('Name', bool(profile['name'])),
        ('Contact', bool(profile['email'] or profile['location'])),
        ('Target role', bool(profile['target_role'])),
        ('Skills', bool(profile['skills'])),
        ('Experience', bool(profile['experience'])),
        ('Education', bool(profile['education_items'])),
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
    profile['input_mode'] = 'file'
    return _normalise(profile)


def parse_resume_image(file_objs) -> dict:
    """Build a candidate profile from one or more resume screenshot images.

    This is the privacy-preserving alternative to parse_resume(): the candidate
    can crop out the personal-info section of their resume (name, photo, email,
    phone, address) and upload only the remaining part(s) as image files.
    """
    file_objs = list(file_objs or [])
    if not file_objs:
        raise ValueError('Upload at least one resume screenshot.')
    if len(file_objs) > MAX_RESUME_IMAGES:
        raise ValueError(f'Upload at most {MAX_RESUME_IMAGES} screenshots at a time.')

    images: list[tuple[bytes, str]] = []
    for file_obj in file_objs:
        suffix = Path(file_obj.name).suffix.lower()
        mime = IMAGE_SUFFIX_MIME.get(suffix)
        if mime is None:
            raise ValueError('Unsupported image format. Use PNG, JPG or WEBP screenshots.')
        data = bytes(file_obj.getbuffer())
        if not data:
            raise ValueError(f'"{file_obj.name}" appears to be empty.')
        if len(data) > MAX_IMAGE_BYTES:
            raise ValueError(f'"{file_obj.name}" is larger than 10 MB.')
        images.append((data, mime))

    profile = generate_json_from_images(
        RESUME_PARSE_IMAGE_PROMPT,
        RESUME_PARSE_SCHEMA,
        images,
    )

    profile['source'] = 'live'
    profile['input_mode'] = 'image_partial'
    return _normalise(profile)