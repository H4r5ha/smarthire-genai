"""Centralized LLM prompts and response schemas used by SmartHire."""


# Resume parsing prompt used by parse_resume() to extract a structured candidate
# profile from uploaded resume text without inventing unsupported information.
RESUME_PARSE_PROMPT = """You are a resume information extraction system. Extract only information supported by the resume text.
Do not invent employers, dates, degrees, skills, metrics, email addresses or locations. Use empty strings/empty lists when evidence is absent.
Choose target_role from the strongest role signal in the resume; if absent, infer a conservative role from explicit experience/skills without inventing a seniority level.
Also extract, when present: formal certifications/licenses (certifications) and honors/awards/publications/volunteer or extracurricular leadership highlights (achievements). Leave these as empty lists when the resume has none.
Return valid JSON matching the supplied schema.

RESUME TEXT:
{resume_text}
"""


# JSON schema returned by the resume parsing LLM call in parse_resume().
RESUME_PARSE_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'email': {'type': 'string'},
        'location': {'type': 'string'},
        'target_role': {'type': 'string'},
        'experience_years': {'type': 'number'},
        'education': {'type': 'string'},
        'skills': {
            'type': 'array',
            'items': {'type': 'string'},
        },
        'experience': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'company': {'type': 'string'},
                    'period': {'type': 'string'},
                    'points': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                },
                'required': [
                    'title',
                    'company',
                    'period',
                    'points',
                ],
            },
        },
        'education_items': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'degree': {'type': 'string'},
                    'school': {'type': 'string'},
                    'period': {'type': 'string'},
                    'detail': {'type': 'string'},
                },
                'required': [
                    'degree',
                    'school',
                    'period',
                    'detail',
                ],
            },
        },
        'projects': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'tech': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                },
                'required': [
                    'name',
                    'description',
                    'tech',
                ],
            },
        },
        'summary': {'type': 'string'},
        'certifications': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'issuer': {'type': 'string'},
                    'year': {'type': 'string'},
                },
                'required': [
                    'name',
                    'issuer',
                    'year',
                ],
            },
        },
        'achievements': {
            'type': 'array',
            'items': {'type': 'string'},
        },
    },
    'required': [
        'name',
        'email',
        'location',
        'target_role',
        'experience_years',
        'education',
        'skills',
        'experience',
        'education_items',
        'projects',
        'summary',
        'certifications',
        'achievements',
    ],
}


# CV improvement prompt used by generate() to compare a candidate profile
# against a target job and produce grounded ATS-focused improvements.
RESUME_CV_PROMPT = """You are SmartHire's ATS-focused CV improvement specialist.
Use ONLY the candidate profile and target job evidence below. Never invent qualifications, employers, metrics, dates, technologies, certifications, projects, responsibilities, or outcomes.

Tasks:
1. Extract job_requirements: the concrete skills/technologies/qualifications the target job is explicitly asking for (from its skills field and description). List them as short labels, most important first. This must come only from the target job evidence, never from the candidate profile.
2. Compare the candidate profile against those job_requirements. List matched_skills: the exact skills already on the candidate profile that also appear in job_requirements (use the candidate's own wording). Everything in job_requirements that is NOT in matched_skills belongs in missing_skills instead — the two lists must be evidence-consistent with each other and with `matched`/`missing_count` (matched = length of matched_skills, missing_count = length of missing_skills). Do not report a missing skill the candidate profile already lists, and do not claim a match that isn't a real skill overlap.
3. Set readiness as your honest overall assessment (0-100) of how ready this resume is for this specific job, considering both the skill coverage above and the strength/relevance of the existing experience and projects. It does not have to equal the raw skill-coverage percentage, but a resume with zero matched skills against several required skills must score low (well under 40), and you must be able to justify the number from what is in why_skills.
4. Set has_summary to true only if the candidate profile's `summary` field is non-empty; otherwise false.
5. Rewrite the professional summary to be concise, role-targeted, and ATS-friendly while preserving facts. If has_summary is false, instead compose a short suggested summary built only from facts already present elsewhere in the profile (skills, experience, education) and say so in `why_skills`-adjacent context — never invent experience to fill it.
6. Rewrite selected experience/internship/job bullets only when the source profile provides a corresponding experience item. Improve action verbs, clarity, keyword alignment, and ATS readability without inventing metrics.
7. Rewrite selected project descriptions only when projects are present. Keep all technologies and claims grounded in the source profile.
8. Rewrite certification entries only when the candidate profile's `certifications` list is non-empty (certification_rewrites); otherwise return an empty list.
9. Rewrite achievement/honor/award entries only when the candidate profile's `achievements` list is non-empty (achievement_rewrites); otherwise return an empty list.
10. Produce a clean ATS-friendly skills-section suggestion using only skills already present plus clearly labelled missing skills from the job.
11. Point out concrete resume issues such as vague wording, missing keywords, inconsistent naming, weak bullet structure, duplicated skills, or missing project/experience detail. Do not claim a formatting issue that is not visible in the supplied profile.
12. Provide practical, prioritised recommendations for what to learn or change next. These must map directly onto the missing_skills list you produced (e.g. which to learn first and why) plus any truthful, non-skill ways to strengthen the resume (structure, evidence, keywords). Do not recommend a skill that is not in missing_skills.
13. Extract soft_skills_from_jd: the interpersonal/behavioural qualities the target job description explicitly or implicitly asks for (e.g. communication, collaboration, ownership, leadership, adaptability, problem-solving, time management, stakeholder management). Unlike technical skills, these do not require new training, so the candidate can usually add them honestly right away. For each one, give `how_to_add`: a concrete, truthful way to surface it on the resume — prefer pointing at an existing bullet/experience/project in the candidate profile that already demonstrates it (name it), and only fall back to suggesting a short "Core Strengths"-style addition when nothing in the profile evidences it yet. Never fabricate a specific accomplishment to justify a soft skill.

Return JSON matching the schema exactly.

CANDIDATE PROFILE:
{profile}

TARGET JOB:
{job}
"""


# JSON schema returned by the CV improvement LLM call in generate().
CV_SCHEMA = {
    'type': 'object',
    'properties': {
        'readiness': {'type': 'integer'},
        'matched': {'type': 'integer'},
        'missing_count': {'type': 'integer'},
        'job_requirements': {
            'type': 'array',
            'items': {'type': 'string'},
        },
        'matched_skills': {
            'type': 'array',
            'items': {'type': 'string'},
        },
        'missing_skills': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'skill': {'type': 'string'},
                    'priority': {'type': 'string'},
                },
                'required': [
                    'skill',
                    'priority',
                ],
            },
        },
        'why_skills': {'type': 'string'},
        'has_summary': {'type': 'boolean'},
        'summary': {'type': 'string'},
        'bullets': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'before': {'type': 'string'},
                    'after': {'type': 'string'},
                    'why': {'type': 'string'},
                },
                'required': [
                    'before',
                    'after',
                    'why',
                ],
            },
        },
        'experience_rewrites': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'role': {'type': 'string'},
                    'company': {'type': 'string'},
                    'before': {'type': 'string'},
                    'after': {'type': 'string'},
                    'why': {'type': 'string'},
                },
                'required': [
                    'role',
                    'company',
                    'before',
                    'after',
                    'why',
                ],
            },
        },
        'project_rewrites': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'project': {'type': 'string'},
                    'before': {'type': 'string'},
                    'after': {'type': 'string'},
                    'why': {'type': 'string'},
                },
                'required': [
                    'project',
                    'before',
                    'after',
                    'why',
                ],
            },
        },
        'certification_rewrites': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'certification': {'type': 'string'},
                    'before': {'type': 'string'},
                    'after': {'type': 'string'},
                    'why': {'type': 'string'},
                },
                'required': [
                    'certification',
                    'before',
                    'after',
                    'why',
                ],
            },
        },
        'achievement_rewrites': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'achievement': {'type': 'string'},
                    'before': {'type': 'string'},
                    'after': {'type': 'string'},
                    'why': {'type': 'string'},
                },
                'required': [
                    'achievement',
                    'before',
                    'after',
                    'why',
                ],
            },
        },
        'skills_section': {
            'type': 'object',
            'properties': {
                'recommended': {
                    'type': 'array',
                    'items': {'type': 'string'},
                },
                'missing_to_add_after_learning': {
                    'type': 'array',
                    'items': {'type': 'string'},
                },
                'why': {'type': 'string'},
            },
            'required': [
                'recommended',
                'missing_to_add_after_learning',
                'why',
            ],
        },
        'resume_issues': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'issue': {'type': 'string'},
                    'severity': {'type': 'string'},
                    'fix': {'type': 'string'},
                },
                'required': [
                    'issue',
                    'severity',
                    'fix',
                ],
            },
        },
        'recommendations': {
            'type': 'array',
            'items': {'type': 'string'},
        },
        'soft_skills_from_jd': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'skill': {'type': 'string'},
                    'why_relevant': {'type': 'string'},
                    'how_to_add': {'type': 'string'},
                },
                'required': [
                    'skill',
                    'why_relevant',
                    'how_to_add',
                ],
            },
        },
    },
    'required': [
        'readiness',
        'matched',
        'missing_count',
        'job_requirements',
        'matched_skills',
        'missing_skills',
        'why_skills',
        'has_summary',
        'summary',
        'bullets',
        'experience_rewrites',
        'project_rewrites',
        'certification_rewrites',
        'achievement_rewrites',
        'skills_section',
        'resume_issues',
        'recommendations',
        'soft_skills_from_jd',
    ],
}


# Career mentor prompt used by the mentor RAG chain to answer career questions
# using retrieved job and career-note evidence while grounding the response.
MENTOR_PROMPT = """You are SmartHire Career Mentor. Answer using the retrieved evidence first and use the candidate profile only to personalise the answer.

Rules:
- Treat career notes and job postings as the factual knowledge base.
- Never invent personal facts, experience, technologies, certifications, salaries, employers, hiring probabilities, or unsupported requirements.
- For career-path, roadmap, progression, or "how do I become X?" questions, prefer a retrieved role-specific career note and turn its explicit stages into a practical progression.
- For "what skills should I learn next?", prioritise explicit target-job gaps and support them with retrieved evidence.
- Clearly distinguish conceptual career guidance from requirements observed in job postings.
- Cite the evidence inline as [S1], [S2], etc.
- Keep responses concise: target 80-140 words, use at most 4 short bullets when useful, and avoid long introductions or repeated conclusions.
- Fully answer every part of the user's question. Do not stop after a heading, fragment, or introductory clause; complete every sentence and bullet before ending.
- Only say that the knowledge base lacks enough evidence when it genuinely does.

CANDIDATE PROFILE:
{profile}

RETRIEVED EVIDENCE:
{evidence}

USER QUESTION:
{question}
"""


# Deliberately weaker mentor prompt used only for the evaluation prompt
# comparison. It intentionally omits the stronger grounding and evidence rules.
MENTOR_BEFORE_PROMPT = """You are a career mentor. Answer the user's question clearly and provide practical career advice.

Use the candidate profile and any retrieved information when useful. Be concise and helpful.

CANDIDATE PROFILE:
{profile}

RETRIEVED EVIDENCE:
{evidence}

USER QUESTION:
{question}
"""


# Judge prompt used by the evaluation script to score real mentor responses.
# It evaluates correctness, grounding, and helpfulness on a 1-5 scale.
EVALUATION_JUDGE_PROMPT = """You are an evaluation judge for SmartHire's career mentor chatbot.

Score the mentor response from 1 to 5 on each dimension.

1. Correctness:
- 5 = fully correct and consistent with the supplied evidence
- 4 = mostly correct with only minor issues
- 3 = partly correct or incomplete
- 2 = significant factual or reasoning problems
- 1 = substantially incorrect

2. Grounding:
- 5 = claims are well supported by the supplied evidence, with no unsupported factual claims
- 4 = mostly grounded with a minor unsupported detail
- 3 = mixed grounding; some claims are not clearly supported
- 2 = substantial unsupported content
- 1 = largely ungrounded or contradicts the evidence

3. Helpfulness:
- 5 = directly answers the question with practical, relevant guidance
- 4 = useful and mostly complete
- 3 = somewhat useful but incomplete or generic
- 2 = minimally useful
- 1 = unhelpful or fails to address the question

For deliberately out-of-scope questions, judge whether the mentor appropriately refused the request.
A concise refusal that avoids unsupported claims should receive a high correctness and grounding score.
Do not penalise a correct refusal merely because it does not provide career advice.

Return JSON matching the supplied schema exactly.

QUESTION:
{question}

EXPECTED SCOPE:
{expected_scope}

MENTOR RESPONSE:
{answer}

RETRIEVED EVIDENCE:
{evidence}
"""