from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from .. import config
from ..generate.prompts import MENTOR_PROMPT
from ..llm.gemini_client import generate_text
from ..safety.guardrails import check_input
from ..search.embed import embed_texts
from ..search.job_search import _search_vectors, load_index


ROLE_ALIASES = {
    "data scientist": ["data scientist", "data science"],
    "data analyst": ["data analyst", "data analytics"],
    "machine learning engineer": ["machine learning engineer", "ml engineer"],
    "software engineer": ["software engineer", "software developer"],
}


CAREER_NOTE_ROLE_TERMS = {
    "data scientist": ("data science", "data scientist"),
    "data analyst": ("data analytics", "data analyst"),
    "machine learning engineer": ("machine learning", "ml engineer"),
    "software engineer": ("software engineering", "software engineer"),
}


@lru_cache(maxsize=1)
def _career_notes_cached() -> tuple[dict, ...]:
    notes_dir = Path(__file__).resolve().parents[2] / "data" / "career_notes"
    notes: list[dict] = []

    for path in sorted(notes_dir.glob("*.md")):
        notes.append(
            {
                "title": path.stem.replace("_", " ").title(),
                "type": "Career note",
                "text": path.read_text(encoding="utf-8"),
            }
        )

    return tuple(notes)


def _career_notes() -> list[dict]:
    return list(_career_notes_cached())


@lru_cache(maxsize=1)
def _career_note_embeddings():
    notes = _career_notes_cached()
    if not notes:
        return None
    return embed_texts([note["text"] for note in notes])


def _tokens(text: str) -> set[str]:
    return set(
        token
        for token in re.findall(
            r"[a-zA-Z][a-zA-Z+#./-]{1,}",
            text.lower(),
        )
        if len(token) > 2
    )


def _role_from_question(question: str) -> str | None:
    q = question.lower()

    for role, aliases in ROLE_ALIASES.items():
        if any(alias in q for alias in aliases):
            return role

    return None


def _is_path_question(question: str) -> bool:
    q = question.lower()

    return any(
        term in q
        for term in (
            "career path",
            "career progression",
            "roadmap",
            "how do i become",
            "how to become",
            "path to becoming",
            "progression",
        )
    )


def _note_priority(question: str, note: dict) -> float:
    role = _role_from_question(question)

    if not role:
        return 0.0

    title = str(note.get("title", "")).lower()
    text = str(note.get("text", "")).lower()
    terms = CAREER_NOTE_ROLE_TERMS[role]

    score = 0.0

    if any(term in title for term in terms):
        score += 1.0

    if any(term in text for term in terms):
        score += 0.35

    if _is_path_question(question) and any(
        term in text
        for term in (
            "career path",
            "progression",
            "stage 1",
            "stage 2",
            "stage 3",
        )
    ):
        score += 0.8

    return score


def _retrieve(
    question: str,
    profile: dict | None = None,
    context: dict | None = None,
    k: int = 5,
) -> list[dict]:
    job_index, jobs = load_index()
    notes = _career_notes()

    query = question.strip()
    query_vec = embed_texts([query])[0]
    q_tokens = _tokens(query)

    evidence: list[dict] = []

    scores, indices = _search_vectors(
        job_index,
        query_vec.reshape(1, -1),
        min(k, len(jobs)),
    )

    for score, idx in zip(scores, indices):
        idx = int(idx)

        if idx < 0 or idx >= len(jobs):
            continue

        job = jobs[idx]

        searchable = (
            f"{job.title} "
            f"{job.category} "
            f"{job.skills} "
            f"{job.description}"
        )

        lexical = len(q_tokens & _tokens(searchable))

        relevance = (
            0.80 * float(score)
            + 0.20
            * min(
                lexical / max(1, min(len(q_tokens), 8)),
                1.0,
            )
        )

        evidence.append(
            {
                "title": f"{job.title} - {job.company}",
                "type": "Job posting",
                "relevance": round(
                    max(
                        0,
                        min(
                            100,
                            relevance * 100,
                        ),
                    )
                ),
                "text": job.text,
            }
        )

    if notes:
        note_vectors = _career_note_embeddings()
        similarities = note_vectors @ query_vec
        note_rank: list[tuple[float, int]] = []

        for i, sim in enumerate(similarities):
            lexical = len(
                q_tokens & _tokens(notes[i]["text"])
            )

            base = (
                0.75 * float(sim)
                + 0.25
                * min(
                    lexical / max(1, min(len(q_tokens), 8)),
                    1.0,
                )
            )

            role_bonus = _note_priority(
                query,
                notes[i],
            )

            score = base + 0.30 * role_bonus
            note_rank.append((score, i))

        note_rank.sort(reverse=True)

        # Always surface the best role-specific career note for an explicit
        # career-path query, even when generic semantic similarity is lower.
        role = _role_from_question(query)

        if role and _is_path_question(query):
            role_specific = [
                (score, i)
                for score, i in note_rank
                if _note_priority(query, notes[i]) >= 1.0
            ]

            if role_specific:
                first = role_specific[0][1]
                ordered = [
                    first
                ] + [
                    i
                    for _, i in note_rank
                    if i != first
                ]
            else:
                ordered = [
                    i
                    for _, i in note_rank
                ]
        else:
            ordered = [
                i
                for _, i in note_rank
            ]

        for i in ordered[: min(2, len(notes))]:
            score = next(
                score
                for score, idx in note_rank
                if idx == i
            )

            evidence.append(
                {
                    "title": notes[i]["title"],
                    "type": notes[i]["type"],
                    "relevance": round(
                        max(
                            0,
                            min(
                                100,
                                score * 100,
                            ),
                        )
                    ),
                    "text": notes[i]["text"],
                }
            )

    evidence.sort(
        key=lambda item: item["relevance"],
        reverse=True,
    )

    # Ensure an explicit role-specific path note remains in the final evidence
    # set even if several highly similar job postings outrank it numerically.
    role = _role_from_question(query)

    if role and _is_path_question(query):
        role_note = next(
            (
                item
                for item in evidence
                if item["type"] == "Career note"
                and _note_priority(query, item) >= 1.0
            ),
            None,
        )

        trimmed = evidence[: k + 1]

        if role_note and role_note not in trimmed:
            trimmed = [
                role_note
            ] + [
                item
                for item in trimmed
                if item is not role_note
            ]

            trimmed = trimmed[: k + 1]

        return trimmed

    return evidence[: k + 1]


def _has_role_path_evidence(
    question: str,
    evidence: list[dict],
) -> bool:
    role = _role_from_question(question)

    if not role or not _is_path_question(question):
        return False

    terms = CAREER_NOTE_ROLE_TERMS[role]

    return any(
        item.get("type") == "Career note"
        and any(
            term in str(item.get("text", "")).lower()
            for term in terms
        )
        and "stage 1"
        in str(item.get("text", "")).lower()
        for item in evidence
    )


def _guardrail_step(data: dict[str, Any]) -> dict[str, Any]:
    """Step 1: validate the user's question before any retrieval or LLM call."""
    question = str(data.get("question", ""))

    ok, reason = check_input(
        question,
        scope="mentor",
    )

    if not ok:
        return {
            **data,
            "blocked": True,
            "result": {
                "answer": reason,
                "sources": [],
                "refused": True,
                "source": "live",
                "pipeline_trace": [
                    "Guardrail",
                    "Rejected",
                ],
            },
        }

    return {
        **data,
        "blocked": False,
    }


def _retrieve_step(data: dict[str, Any]) -> dict[str, Any]:
    """Step 2: retrieve evidence and apply the evidence gate."""
    if data.get("blocked"):
        return data

    question = str(data.get("question", ""))
    profile = data.get("profile")
    context = data.get("context")
    k = config.TOP_K_MENTOR

    evidence = _retrieve(
        question,
        profile=profile,
        context=context,
        k=k,
    )

    path_evidence = _has_role_path_evidence(
        question,
        evidence,
    )

    best_relevance = max(
        (
            item["relevance"]
            for item in evidence
        ),
        default=0,
    )

    if not evidence:
        return {
            **data,
            "blocked": True,
            "result": {
                "answer": (
                    "The knowledge base does not contain "
                    "enough evidence to answer this question."
                ),
                "sources": [],
                "refused": True,
                "source": "live",
                "pipeline_trace": [
                    "Guardrail",
                    "Retrieve",
                    "Evidence Gate",
                    "Decline",
                ],
            },
        }

    if (
        best_relevance < config.MENTOR_MIN_SCORE * 100
        and not path_evidence
    ):
        return {
            **data,
            "blocked": True,
            "result": {
                "answer": (
                    "The knowledge base does not contain "
                    "enough evidence to answer this question."
                ),
                "sources": [],
                "refused": True,
                "source": "live",
                "pipeline_trace": [
                    "Guardrail",
                    "Retrieve",
                    "Evidence Gate",
                    "Decline",
                ],
            },
        }

    return {
        **data,
        "evidence": evidence,
        "blocked": False,
    }


def _build_prompt_step(data: dict[str, Any]) -> dict[str, Any]:
    """Step 3: construct the grounded mentor prompt from the retrieved evidence."""
    if data.get("blocked"):
        return data

    question = str(data.get("question", ""))
    profile = data.get("profile")
    context = data.get("context") or {}
    evidence = data.get("evidence", [])

    source_map = {
        f"S{i + 1}": item
        for i, item in enumerate(evidence)
    }

    evidence_blob = "\n\n".join(
        f'[{key}] {item["title"]} ({item["type"]})\n'
        f'{item["text"][:5000]}'
        for key, item in source_map.items()
    )

    target_job = context.get("target_job") or {}
    cv_result = context.get("cv_result") or {}

    candidate_context = {
        **(profile or {}),
        "target_job": {
            key: target_job.get(key, "")
            for key in (
                "title",
                "company",
                "location",
                "skills",
                "description",
            )
        },
        "identified_missing_skills": [
            item.get("skill")
            for item in cv_result.get(
                "missing_skills",
                [],
            )
        ],
        "prior_recommendations": cv_result.get(
            "recommendations",
            [],
        ),
    }

    prompt = MENTOR_PROMPT.format(
        profile=candidate_context,
        evidence=evidence_blob,
        question=question,
    )

    return {
        **data,
        "prompt": prompt,
        "source_map": source_map,
        "blocked": False,
    }


def _mentor_answer_needs_retry(answer: str) -> bool:
    """Detect a likely truncated mentor response before returning it to users."""
    text = str(answer or "").strip()
    if not text:
        return True

    words = text.split()
    last_line = next(
        (line.strip() for line in reversed(text.splitlines()) if line.strip()),
        "",
    )

    # The model occasionally stops immediately after introducing a section,
    # e.g. "Shared skills: Both roles". Treat short, non-terminal answers as
    # incomplete and give Gemini one chance to rewrite the answer completely.
    looks_unfinished = (
        len(words) < 35
        and not last_line.endswith((".", "!", "?", ":", ")", "]"))
        or last_line.endswith(("Both roles", "They share", "The roles"))
        or last_line.endswith(("and", "or", "but", "because", "while"))
    )

    return looks_unfinished


def _llm_step(data: dict[str, Any]) -> dict[str, Any]:
    """Step 4: call Gemini and recover once from a likely truncated answer."""
    if data.get("blocked"):
        return data

    answer = generate_text(
        data["prompt"],
        max_output_tokens=1400,
    )

    if _mentor_answer_needs_retry(answer):
        retry_prompt = (
            f"{data['prompt']}\n\n"
            "IMPORTANT: The previous response appears incomplete. Rewrite the answer "
            "from the beginning and answer every part of the user's question. "
            "Do not stop after a heading or introductory clause. Keep it concise "
            "(about 80-140 words), and finish every sentence and bullet."
        )
        answer = generate_text(
            retry_prompt,
            max_output_tokens=1400,
        )

    return {
        **data,
        "answer": answer.strip(),
        "blocked": False,
    }


def _format_output_step(data: dict[str, Any]) -> dict[str, Any]:
    """Step 5: return the same public response structure as the previous ask()."""
    if data.get("blocked"):
        return data["result"]

    evidence = data.get("evidence", [])
    answer = data.get("answer", "")

    return {
        "answer": answer,
        "sources": [
            {
                "title": item["title"],
                "type": item["type"],
                "relevance": item["relevance"],
            }
            for item in evidence
        ],
        # Internal evidence is retained so evaluation can judge the exact
        # retrieved context without performing a second embedding/retrieval pass.
        "evaluation_evidence": evidence,
        "refused": False,
        "source": "live",
        "pipeline_trace": [
            "Guardrail",
            "Query",
            "Embed",
            "FAISS",
            "Evidence Gate",
            "Gemini",
        ],
    }


# Runnable 1: guardrail validation before retrieval or generation.
_guardrail_runnable = RunnableLambda(_guardrail_step)

# Runnable 2: semantic retrieval plus evidence gating.
_retrieve_runnable = RunnableLambda(_retrieve_step)

# Runnable 3: grounded prompt construction.
_prompt_runnable = RunnableLambda(_build_prompt_step)

# Runnable 4: Gemini generation.
_llm_runnable = RunnableLambda(_llm_step)

# Runnable 5: final response formatting.
_output_runnable = RunnableLambda(_format_output_step)


# Real LCEL pipeline:
# Guardrail -> Retrieve -> Prompt -> Gemini -> Output
mentor_chain = (
    RunnablePassthrough()
    | _guardrail_runnable
    | _retrieve_runnable
    | _prompt_runnable
    | _llm_runnable
    | _output_runnable
)


def ask(
    question: str,
    profile: dict | None,
    history: list[dict],
    context: dict | None = None,
) -> dict:
    """Run the five-stage LCEL mentor pipeline.

    The history argument is retained for compatibility with the existing
    Streamlit application and current function signature.
    """
    del history

    return mentor_chain.invoke(
        {
            "question": question,
            "profile": profile,
            "context": context,
        }
    )


def status() -> dict:
    return {
        "rag_online": bool(config.GEMINI_API_KEY),
        "guardrails": True,
    }