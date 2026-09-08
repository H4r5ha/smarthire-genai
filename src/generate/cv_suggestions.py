from __future__ import annotations

import json

from ..llm.gemini_client import generate_json
from ..safety.guardrails import check_input
from .prompts import CV_SCHEMA, RESUME_CV_PROMPT


def generate(profile: dict, job: dict) -> dict:
    prompt = RESUME_CV_PROMPT.format(
        profile=json.dumps(profile, ensure_ascii=False),
        job=json.dumps(job, ensure_ascii=False),
    )

    allowed, message = check_input(prompt, scope='resume')
    if not allowed:
        raise ValueError(f'CV improvement could not be generated: {message}')

    result = generate_json(prompt, CV_SCHEMA)

    result['source'] = 'live'

    # Force every count shown on the CV Improvement page to come from the
    # actual lists the model returned, rather than trusting separately
    # generated numbers that can drift out of sync with them (this is what
    # previously let the page show "0 matched / 8 missing" next to an
    # unrelated 20% readiness figure).
    result['job_requirements'] = result.get('job_requirements', []) or []
    result['matched_skills'] = result.get('matched_skills', []) or []
    result['missing_skills'] = result.get('missing_skills', []) or []
    result['matched'] = len(result['matched_skills'])
    result['missing_count'] = len(result['missing_skills'])

    total_requirements = result['matched'] + result['missing_count']
    if total_requirements > 0:
        # Readiness is deliberately computed here, from the same matched/missing
        # counts shown next to it, instead of trusting a separately generated
        # number. That separation is exactly what previously let the page show
        # "0 matched / 8 missing" beside an unrelated 20% readiness figure.
        result['readiness'] = round(100 * result['matched'] / total_requirements)
    else:
        # No explicit requirements could be extracted (e.g. a very short pasted
        # JD) — nothing to compute a skill-coverage ratio against, so fall back
        # to the model's holistic read of the profile, still clamped.
        result['readiness'] = max(0, min(100, int(result.get('readiness', 0) or 0)))

    result['has_summary'] = bool(result.get('has_summary', bool(profile.get('summary'))))
    result['bullets'] = result.get('bullets', []) or []
    result['experience_rewrites'] = result.get('experience_rewrites', []) or []
    result['project_rewrites'] = result.get('project_rewrites', []) or []
    result['certification_rewrites'] = result.get('certification_rewrites', []) or []
    result['achievement_rewrites'] = result.get('achievement_rewrites', []) or []
    result['skills_section'] = (
        result.get('skills_section')
        or {
            'recommended': list(profile.get('skills', [])),
            'missing_to_add_after_learning': [],
            'why': 'Keep the skills section factual and role-relevant.',
        }
    )
    result['resume_issues'] = result.get('resume_issues', []) or []
    result['recommendations'] = result.get('recommendations', []) or []
    result['soft_skills_from_jd'] = result.get('soft_skills_from_jd', []) or []

    # "Before" is the plain skill-coverage score computed above. "After" is a
    # deterministic projection of what the *free* edits on this page alone
    # (no new skills actually learned yet) could realistically buy back:
    # naming the soft skills the JD wants, tightening the skills section, and
    # rewriting summary/bullets/projects/certs/achievements for keyword
    # alignment. It is derived from the size of what was actually generated
    # here (never from a separate LLM-guessed number) so it can't drift out
    # of sync with the content shown just below it, and it is deliberately
    # capped short of 100 — closing the remaining gap still requires learning
    # the missing_skills listed above.
    before = result['readiness']
    rewrite_credits = (
        len(result['bullets'])
        + len(result['experience_rewrites'])
        + len(result['project_rewrites'])
        + len(result['certification_rewrites'])
        + len(result['achievement_rewrites'])
        + (1 if result.get('summary') else 0)
    )
    bonus = min(10, 2 * len(result['soft_skills_from_jd']))
    bonus += min(10, rewrite_credits)
    bonus += 5 if (result['skills_section'] or {}).get('recommended') else 0
    bonus = min(bonus, max(0, 100 - before))
    result['ats_score_before'] = before
    result['ats_score_after'] = min(95, before + bonus)
    return result