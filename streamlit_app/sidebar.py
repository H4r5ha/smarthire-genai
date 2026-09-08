"""Persistent left sidebar."""
from __future__ import annotations

import streamlit as st

from . import backend, config as C, state
from .components import esc, md


def _nav_button(page: str) -> None:
    active = state.current_page() == page
    if st.button(
        page,
        key=f"nav_{page}",
        type="primary" if active else "secondary",
        use_container_width=True,
    ):
        state.go_to(page)
        st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        md(
            '<div class="sh-brand"><div class="logo">✦</div>'
            f'<div><div class="name">{C.APP_NAME}</div><div class="sub">GENAI PORTAL</div></div></div>'
        )

        md('<div class="sh-section workflow-section">WORKFLOW</div>')
        for page in C.WORKFLOW_PAGES:
            _nav_button(page)

        # Project/Data & Index/Evaluation navigation has intentionally been removed
        # from the sidebar. The underlying pages remain in the application for
        # development/evaluation access, but they are no longer part of the user-facing nav.

        p = state.profile()
        if p:
            sample = '<span class="badge sample" style="margin-left:.4rem">SAMPLE</span>' if p.get("source") == "sample" else ""
            md(
                '<div class="sh-side-card"><div class="who">'
                f'<div class="avatar">{esc(p.get("initial", "?"))}</div>'
                f'<div><div class="n">{esc(p.get("name", "Candidate"))}{sample}</div>'
                f'<div class="r">{esc(p.get("target_role", "Target role not set"))}</div></div></div>'
                f'<div class="ok"><span class="dot g"></span>Profile ready · {len(p.get("skills", []))} skills</div></div>'
            )
        else:
            md(
                '<div class="sh-side-card"><div class="lbl">CANDIDATE</div>'
                '<div class="empty"><b style="color:#E6E8F0">No candidate profile</b><br>Upload a resume to begin</div></div>'
            )

        idx = backend.get_index_status()
        vector_ready = next((i["ready"] for i in idx if i["name"] == "FAISS Index"), False)
        mentor = backend.get_mentor_status()
        md(
            '<div class="sh-side-card"><div class="lbl">SYSTEM</div>'
            f'<div class="row"><span>Vector index</span><span><span class="dot {"g" if vector_ready else "a"}"></span>{"Ready" if vector_ready else "Not built"}</span></div>'
            f'<div class="row"><span>Mentor RAG</span><span><span class="dot {"g" if mentor["rag_online"] else "r"}"></span>{"Online" if mentor["rag_online"] else "Offline"}</span></div>'
            '</div>'
        )

        md('<div class="sh-section" style="margin-top:1rem">DEMO MODE</div>')
        demo = st.toggle(
            "Sample-data preview",
            value=st.session_state[C.SS_DEMO_MODE],
            key="demo_toggle",
            help="Fills every page with clearly labelled SAMPLE data.",
        )
        if demo != st.session_state[C.SS_DEMO_MODE]:
            st.session_state[C.SS_DEMO_MODE] = demo
            if demo:
                st.session_state[C.SS_PROFILE] = backend.parse_resume(None, demo=True)
                st.session_state[C.SS_PROFILE_STATE] = "ready"
            else:
                state.clear_profile()
            st.rerun()

        md(
            '<div style="font-size:11px;color:#7D8499;margin:.2rem .3rem 0 .3rem;line-height:1.4">'
            'Sample data is illustrative only and is always labelled SAMPLE.</div>'
        )
