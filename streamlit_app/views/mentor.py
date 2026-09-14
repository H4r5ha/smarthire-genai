"""Page 4 - AI Career Mentor (RAG chat UI)."""
from __future__ import annotations

from datetime import datetime
import hashlib

import streamlit as st

from .. import backend, config as C, sample_data as sd, state
from ..components import empty_state, esc, horizontal_pipeline, md, page_header, sample_badge


def _selected_role() -> str:
    """Resolve the role the user is currently working with.

    Priority:
    1. Explicit target job selected from Job Match.
    2. Current Job Match search query (important when the user clicked
       a Suggested Role but has not yet targeted a specific opening).
    3. Parsed profile target role.
    4. Safe generic fallback.
    """
    target_job = st.session_state.get(C.SS_TARGET_JOB) or {}
    target_title = str(target_job.get("title", "") or "").strip()
    if target_title:
        return target_title

    query = str(
        st.session_state.get(C.SS_JOB_QUERY, "") or ""
    ).strip()
    if query:
        return query

    profile = state.profile() or {}
    profile_role = str(
        profile.get("target_role", "") or ""
    ).strip()
    if profile_role:
        return profile_role

    return "your target role"


def _role_family(role: str) -> str:
    """Convert a concrete job title into a clean role family for prompts."""
    text = role.lower()

    aliases = (
        ("data scientist", "Data Scientist"),
        ("data analyst", "Data Analyst"),
        ("machine learning", "Machine Learning Engineer"),
        ("ml engineer", "Machine Learning Engineer"),
        ("artificial intelligence", "AI Engineer"),
        ("ai engineer", "AI Engineer"),
        ("ui/ux", "UI/UX Designer"),
        ("ux designer", "UX Designer"),
        ("product designer", "Product Designer"),
        ("frontend", "Frontend Developer"),
        ("front end", "Frontend Developer"),
        ("backend", "Backend Developer"),
        ("back end", "Backend Developer"),
        ("full stack", "Full Stack Developer"),
        ("software engineer", "Software Engineer"),
        ("software developer", "Software Developer"),
        ("devops", "DevOps Engineer"),
        ("cloud engineer", "Cloud Engineer"),
        ("business analyst", "Business Analyst"),
        ("qa engineer", "QA Engineer"),
        ("quality assurance", "QA Engineer"),
        ("cybersecurity", "Cybersecurity Analyst"),
    )

    for needle, clean_name in aliases:
        if needle in text:
            return clean_name

    return role.strip() or "your target role"


def _suggested_questions() -> list[str]:
    """Generate role-aware questions from the current SmartHire state.

    These are deliberately deterministic: a page rerun does not cause the
    suggestion set to change randomly, but changing the selected role does.
    """
    role = _role_family(_selected_role())

    if role == "Data Scientist":
        questions = [
            "What skills should I strengthen for Data Scientist roles?",
            "What projects would make me a stronger Data Scientist candidate?",
            "How should I prepare for Data Scientist interviews?",
            "What career path can I follow in Data Science?",
            "How can I transition into Data Scientist roles from my current profile?",
        ]
    elif role == "Data Analyst":
        questions = [
            "What skills should I strengthen for Data Analyst roles?",
            "What projects would make me a stronger Data Analyst candidate?",
            "How should I prepare for Data Analyst interviews?",
            "What career path can I follow in Data Analytics?",
            "How can I transition into Data Analyst roles from my current profile?",
        ]
    elif role == "Machine Learning Engineer":
        questions = [
            "What skills should I strengthen for Machine Learning Engineer roles?",
            "What projects would make me a stronger ML Engineer candidate?",
            "How should I prepare for Machine Learning Engineer interviews?",
            "What career path can I follow in Machine Learning Engineering?",
            "How can I transition into ML Engineer roles from my current profile?",
        ]
    elif role in {"UI/UX Designer", "UX Designer", "Product Designer"}:
        questions = [
            f"What skills should I strengthen for {role} roles?",
            f"What projects would make me a stronger {role} candidate?",
            f"How should I prepare for {role} interviews?",
            f"What career path can I follow in {role}?",
            f"How can I transition into {role} roles from my current profile?",
        ]
    else:
        questions = [
            f"What skills should I strengthen for {role} roles?",
            f"What projects would make me a stronger {role} candidate?",
            f"How should I prepare for {role} interviews?",
            f"What career path can I follow in {role}?",
            f"How can I position my current experience for {role} roles?",
        ]

    # Ensure unique widget keys even if role text is unusual.
    return questions


def _question_key(question: str) -> str:
    digest = hashlib.sha1(question.encode("utf-8")).hexdigest()[:10]
    return f"mentor_suggestion_{digest}"


def _status_cards() -> None:
    p = state.profile()
    status = backend.get_mentor_status()

    selected_role = _selected_role()

    if p:
        profile_name = str(p.get("name", "") or "Candidate")
        who = f'{esc(profile_name)} → {esc(_role_family(selected_role))}'
    else:
        who = esc(_role_family(selected_role))

    cards = [
        ("g", "RAG Ready", "Career knowledge loaded"),
        ("g", "Guardrails Active", "Safe & focused responses"),
        ("a", "Your Profile", who),
    ]

    cols = st.columns(3, gap="small")

    for col, (tone, title, subtitle) in zip(
        cols,
        cards,
    ):
        with col:
            md(
                f'<div class="status-card">'
                f'<div class="status-dotbox {tone}">●</div>'
                f'<div><div class="t">{title}</div>'
                f'<div class="s">{subtitle}</div></div>'
                f'</div>'
            )


def _ask(question: str) -> None:
    question = (question or "").strip()

    if not question:
        return

    now = datetime.now().strftime("%I:%M %p")

    st.session_state[C.SS_CHAT].append(
        {
            "role": "user",
            "text": question,
            "ts": now,
        }
    )

    st.session_state[C.SS_MENTOR_STATE] = "thinking"


def _resolve_pending() -> None:
    chat = st.session_state[C.SS_CHAT]

    if not chat or chat[-1]["role"] != "user":
        return

    with st.status(
        "Retrieving career evidence...",
        expanded=False,
    ) as status:
        try:
            target_job = st.session_state.get(
                C.SS_TARGET_JOB
            )
            cv_result = st.session_state.get(
                C.SS_CV_RESULT
            )

            reply = backend.ask_mentor(
                chat[-1]["text"],
                state.profile(),
                chat,
                context={
                    "target_job": target_job,
                    "cv_result": cv_result,
                },
            )

            status.update(
                label="Generating grounded response...",
                state="running",
            )

        except backend.BackendError as exc:
            reply = {
                "answer": str(exc),
                "sources": [],
                "refused": True,
                "source": "error",
            }

        status.update(
            label="Done",
            state="complete",
        )

    chat.append(
        {
            "role": "bot",
            "ts": datetime.now().strftime("%I:%M %p"),
            **reply,
        }
    )

    st.session_state[C.SS_MENTOR_STATE] = "idle"


def _chat_html(chat: list[dict]) -> str:
    if not chat:
        return (
            '<div class="chat-empty">'
            '<div class="chat-empty-icon">✦</div>'
            '<div class="chat-empty-title">'
            'Start a conversation with your career mentor.'
            '</div>'
            '<div class="chat-empty-sub">'
            'Pick a suggested question or type your own below.'
            '</div>'
            '</div>'
        )

    parts: list[str] = []

    for message in chat:
        if message["role"] == "user":
            parts.append(
                f'<div class="msg user">'
                f'<div class="bubble">'
                f'<div class="who">YOU</div>'
                f'{esc(message["text"])}'
                f'<div class="ts">{esc(message["ts"])}</div>'
                f'</div>'
                f'</div>'
            )
        else:
            refused = (
                " refused"
                if message.get("refused")
                else ""
            )

            tag = (
                sample_badge("SAMPLE RESPONSE")
                if message.get("source") == "sample"
                else ""
            )

            parts.append(
                f'<div class="msg bot">'
                f'<div class="bubble{refused}">'
                f'<div class="who">SMARTHIRE MENTOR {tag}</div>'
                f'{esc(message["answer"])}'
                f'<div class="ts">{esc(message["ts"])}</div>'
                f'</div>'
                f'</div>'
            )

    return "".join(parts)


def _sources_html(chat: list[dict]) -> str:
    last_bot = next(
        (
            message
            for message in reversed(chat)
            if message["role"] == "bot"
        ),
        None,
    )

    if not last_bot:
        return (
            '<div class="sources-empty">'
            'Answers are grounded in job descriptions and '
            'career resources. Sources will appear here.'
            '</div>'
        )

    sources = sorted(
        last_bot.get("sources", []),
        key=lambda source: float(
            source.get("relevance", 0)
        ),
        reverse=True,
    )[:4]

    if not sources:
        return (
            '<div class="sources-empty warning">'
            'No supporting evidence was retrieved, so the '
            'mentor declined to answer.'
            '</div>'
        )

    return "".join(
        (
            f'<div class="src">'
            f'<div class="t">'
            f'<span class="n">{index}.</span>'
            f'{esc(source["title"])}'
            f'</div>'
            f'<div class="m">'
            f'<span>Source · {esc(source["type"])}</span>'
            f'<span>Relevance {source["relevance"]}%</span>'
            f'</div>'
            f'<div class="bar">'
            f'<i style="width:{source["relevance"]}%"></i>'
            f'</div>'
            f'</div>'
        )
        for index, source in enumerate(
            sources,
            start=1,
        )
    )


def _input_bar() -> None:
    """Compact ChatGPT-style composer with both controls inside one card.

    Wrapped in an st.form so that: (1) pressing Enter while typing submits
    the question -- a bare st.text_input plus a separate st.button outside
    any form never responds to Enter, only to an actual click on the
    button; and (2) clear_on_submit=True empties the field right after
    sending, instead of leaving the just-asked question sitting there.
    """
    with st.container(border=True, key="mentor_input_bar"):
        with st.form("mentor_form", border=False, clear_on_submit=True):
            left, right = st.columns(
                [12, 0.85],
                gap="small",
                vertical_alignment="center",
            )

            with left:
                prompt = st.text_input(
                    "Career question",
                    placeholder="Ask your career question...",
                    label_visibility="collapsed",
                    key="mentor_question_input",
                )

            with right:
                send = st.form_submit_button(
                    "↑",
                    type="primary",
                    use_container_width=True,
                    key="mentor_send_button",
                )

    if send and prompt.strip():
        _ask(prompt)
        st.rerun()


def _target_job_card(job: dict) -> None:
    """Same TARGET JOB card used on the CV Improvement page, reused here so
    the role the mentor is answering about is always visible at a glance."""
    with st.container(border=True, key="mentor_card_target_job"):
        left, right = st.columns([5.2, 1.1], gap="medium", vertical_alignment="center")
        with left:
            md(
                '<div class="eyebrow">TARGET JOB</div>'
                f'<div class="target-title">{esc(job.get("title", "Untitled role"))}</div>'
                f'<div class="target-meta"><b>{esc(job.get("company", "Unknown company"))}</b> · {esc(job.get("location", "Not specified"))}</div>'
            )
        with right:
            if st.button("Change Job", type="primary", use_container_width=True, key="mentor_change_job"):
                state.go_to(C.PAGE_JOBS)
                st.rerun()
        # Same bottom-breathing-room spacer used on the CV Improvement
        # page's identical card -- without it, the last line (the
        # company/location row) sits flush against the card's border.
        md('<div class="cv-card-edge-space" aria-hidden="true"></div>')


def render() -> None:
    page_header(
        "AI Career Mentor",
        "Your Personal AI Career Mentor",
        "Ask questions, get guidance, and explore career opportunities.",
    )

    job = st.session_state.get(C.SS_TARGET_JOB)
    if job is None and (state.profile_is_sample() or st.session_state.get(C.SS_DEMO_MODE)):
        job = sd.SAMPLE_TARGET_JOB
    if job is not None:
        _target_job_card(job)

    st.markdown(
        '<div style="height:.8rem"></div>',
        unsafe_allow_html=True,
    )

    left, centre, right = st.columns(
        [1, 2.2, 1.05],
        gap="small",
    )

    chat = st.session_state[C.SS_CHAT]

    with left:
        md(
            '<div class="side-section-title">'
            'Suggested Questions'
            '</div>'
        )

        # IMPORTANT: these are generated from the currently selected
        # target/search role, not from the static sample-data list.
        for question in _suggested_questions():
            if st.button(
                question,
                key=_question_key(question),
                use_container_width=True,
            ):
                _ask(question)
                st.rerun()

    with centre:
        md(
            f'<div class="chat-panel">'
            f'{_chat_html(chat)}'
            f'</div>'
        )

    with right:
        md(
            '<div class="sources-panel">'
            '<div class="side-section-title">'
            'Sources & Evidence'
            '</div>'
            f'{_sources_html(chat)}'
            '</div>'
        )

    _input_bar()

    if (
        st.session_state[C.SS_MENTOR_STATE]
        == "thinking"
    ):
        _resolve_pending()
        st.rerun()

    md(
        '<div class="content-card mentor-pipeline">'
        '<div class="card-heading">Retrieval Pipeline '
        '<span class="badge good">RAG PIPELINE</span>'
        '</div>'
        + horizontal_pipeline(sd.RAG_PIPELINE)
        + '</div>'
    )

    md(
        '<div class="mentor-footer">'
        '<div class="mentor-footer-title">'
        'SmartHire GenAI — Resume Matching &amp; AI Career Mentor'
        '</div>'
        '<div class="mentor-footer-copy">'
        'Your career profile, job evidence, and grounded AI '
        'guidance are brought together in one focused workspace.'
        '</div>'
        '<div class="mentor-thanks">'
        'Thank you for visiting SmartHire.'
        '</div>'
        '</div>'
    )