from __future__ import annotations

import re

OFF_TOPIC = {
    'politics',
    'political',
    'election',
    'elections',
    'cryptocurrency trading',
    'medical diagnosis',
    'legal strategy',
    'password',
    'malware',
    'exploit',
    'weapon',
    'self harm',
    'suicide',
    'porn',
}
INJECTION_PATTERNS = [
    r'ignore (all|any|the) (previous|prior) instructions',
    r'forget (all|your) instructions',
    r'reveal (the )?(system|developer) prompt',
    r'jailbreak',
]


def check_input(text: str, *, scope: str = 'career') -> tuple[bool, str]:
    cleaned = ' '.join((text or '').split())
    if len(cleaned) < 3:
        return False, 'Please enter a more specific question.'
    lowered = cleaned.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return False, 'That request is not allowed.'
    for term in OFF_TOPIC:
        if term in lowered:
            return False, 'SmartHire is limited to career, resume, job-search and job-preparation questions.'
    if scope == 'mentor' and len(cleaned) > 1200:
        return False, 'Please keep mentor questions below 1,200 characters.'
    return True, ''
