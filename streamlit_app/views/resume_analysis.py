"""Page 1 - Resume Analysis / SmartHire landing-style front page."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from .. import backend, config as C, state
from ..components import badge, chips, empty_state, error_state, esc, md, sample_badge


PROJECT_TITLE = "SmartHire GenAI — Resume Matching & AI Career Mentor"
PROJECT_COPY = (
    "An end-to-end career workspace that turns a resume into a structured profile, "
    "matched jobs, ATS-focused improvements, and grounded career guidance."
)


# Page-scoped CSS is kept here so this front-page redesign can be dropped into the
# existing project without forcing unrelated pages to change.
FRONT_PAGE_CSS = """
<style>
/* ---------- Front-page project banner ---------- */
.smart-front-hero {
    margin: -0.35rem 0 1.55rem 0;
    padding: 1.75rem 2rem 1.65rem 2rem;
    border-radius: 0 0 20px 20px;
    background: linear-gradient(135deg, #171B2B 0%, #2B245F 52%, #4F46E5 100%);
    box-shadow: 0 16px 34px -20px rgba(79,70,229,.55);
}
.smart-front-hero .title {
    margin: 0;
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(28px, 3vw, 39px);
    line-height: 1.12;
    font-weight: 700;
    letter-spacing: -0.02em;
}
.smart-front-hero .copy {
    max-width: 900px;
    margin: .65rem 0 0 0;
    color: rgba(255,255,255,.84) !important;
    font-size: 14px;
    line-height: 1.65;
}

/* ---------- Front-page uploader ---------- */
.smart-upload-label {
    margin: .15rem 0 .6rem 0;
    color: var(--text);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 600;
}
.smart-upload-shell {
    margin: 0;
    padding: .35rem 0 .15rem 0;
    border-radius: 14px;
}
.smart-upload-note {
    margin-top: -.1rem;
    margin-bottom: .75rem;
    color: var(--muted);
    font-size: 12px;
}
.smart-privacy-note {
    display: flex;
    flex-wrap: wrap;
    gap: .7rem;
    margin: 0 0 .85rem 0;
}
.smart-privacy-option {
    flex: 1 1 260px;
    display: flex;
    align-items: flex-start;
    gap: .65rem;
    padding: .75rem .85rem;
    border-radius: 12px;
    background: #F6F8FD;
    border: 1px solid #E3E9F7;
}
.smart-privacy-option .icon {
    flex: 0 0 auto;
    width: 30px;
    height: 30px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: #FFFFFF;
    background: linear-gradient(135deg, #4F46E5 0%, #7C6CF6 100%);
    box-shadow: 0 4px 10px -4px rgba(79,70,229,.6);
}
.smart-privacy-option .label {
    margin-bottom: .15rem;
    color: var(--text);
    font-size: 12.5px;
    font-weight: 700;
}
.smart-privacy-option .desc {
    color: var(--muted);
    font-size: 11.5px;
    line-height: 1.55;
}
.smart-privacy-option .desc b { color: var(--accent); font-weight: 600; }

/* Make the real Streamlit uploader resemble the supplied reference image. */
[data-testid="stFileUploader"] {
    margin: 0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    min-height: 94px !important;
    padding: .9rem 1.1rem !important;
    background: #F1F3F7 !important;
    border: 1px solid #E4E7EC !important;
    border-radius: 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: .85rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
/* The drag/drop instructions are hidden above (they duplicated the note
   below the box), so this adds a short label to the right of the Browse
   button instead, inside the same box. */
.st-key-resume_dropzone [data-testid="stFileUploaderDropzone"]::after {
    content: "Add a resume file or screenshot(s)";
    color: var(--muted);
    font-size: 12.5px;
    font-weight: 500;
    white-space: nowrap;
}
[data-testid="stFileUploaderDropzone"] button {
    margin-left: .05rem !important;
    min-height: 42px !important;
    padding: .55rem 1.05rem !important;
    border-radius: 10px !important;
    border: 1px solid #D9DDE6 !important;
    background: #FFFFFF !important;
    color: var(--text) !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
[data-testid="stFileUploaderFile"] {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* ---------- Compact centered action row ---------- */
.smart-action-gap {
    height: .55rem;
}
.smart-status {
    min-height: 20px;
    margin: .3rem 0 .85rem 0;
    text-align: center;
    color: var(--muted);
    font-size: 12px;
}
.smart-status-row {
    display: flex;
    align-items: center;
    gap: .5rem;
    margin: .55rem 0 0 0;
    padding: .55rem .8rem;
    border-radius: 10px;
    border: 1px solid transparent;
    font-size: 12.5px;
    color: var(--text);
}
.smart-status-row.is-ok {
    background: #F0FBF6;
    border-color: #CEEEDC;
}
.smart-status-row.is-error {
    background: #FDF1F1;
    border-color: #F5D3D3;
}
.smart-status-row.is-neutral {
    justify-content: center;
    padding: .2rem 0;
    color: var(--muted);
}
.smart-status-row b { font-weight: 600; }

/* ---------- Page title hierarchy ---------- */
.smart-front-kicker {
    margin: 0 0 .35rem 0;
    color: var(--accent);
    font-size: 10px;
    letter-spacing: .19em;
    font-weight: 700;
}
.smart-front-title {
    margin: 0;
    color: var(--text);
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(38px, 4.1vw, 52px);
    line-height: 1.04;
    font-weight: 700;
    letter-spacing: -.025em;
}
.smart-front-subtitle {
    max-width: 780px;
    margin: .55rem 0 1.35rem 0;
    color: var(--muted);
    font-size: 14px;
    line-height: 1.65;
}

/* ---------- Small screens ---------- */
@media (max-width: 800px) {
    .smart-front-hero { padding: 1.35rem 1.2rem; }
    .smart-front-hero .title { font-size: 26px; }
    .smart-front-hero .copy { font-size: 13px; }
    .smart-front-title { font-size: 35px; }
}
</style>
"""


def _front_page_styles() -> None:
    st.markdown(FRONT_PAGE_CSS, unsafe_allow_html=True)


def _project_banner() -> None:
    md(
        '<section class="smart-front-hero">'
        f'<div class="title">{esc(PROJECT_TITLE)}</div>'
        f'<div class="copy">{esc(PROJECT_COPY)}</div>'
        '</section>'
    )


def _page_intro() -> None:
    md(
        '<h1 class="smart-front-title">Resume Analyzer</h1>'
        '<p class="smart-front-subtitle">'
        'Upload a resume to build a validated candidate profile that powers job matching, '
        'CV improvement, and the AI career mentor.'
        '</p>'
    )


DOC_SUFFIXES = {"pdf", "docx", "txt"}
IMAGE_SUFFIXES = {"png", "jpg", "jpeg", "webp"}


def _classify_uploads(files: list) -> tuple[list, list]:
    docs, images = [], []
    for f in files:
        suffix = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
        if suffix in DOC_SUFFIXES:
            docs.append(f)
        elif suffix in IMAGE_SUFFIXES:
            images.append(f)
    return docs, images


def _upload_widget():
    md('<div class="smart-upload-label">Upload your resume</div>')
    md(
        '<div class="smart-privacy-note">'
        '<div class="smart-privacy-option">'
        '<div class="icon">&#128196;</div>'
        '<div><div class="label">Full resume</div>'
        '<div class="desc">Upload your <b>complete resume</b> as a single '
        'PDF, DOCX or TXT file.</div></div>'
        '</div>'
        '<div class="smart-privacy-option">'
        '<div class="icon">&#128274;</div>'
        '<div><div class="label">Privacy mode</div>'
        '<div class="desc">Crop out your name, photo, email, phone and address, '
        'then upload <b>screenshot(s)</b> of just the sections you want parsed '
        '&mdash; like skills or experience.</div></div>'
        '</div>'
        '</div>'
    )
    with st.container(key="resume_dropzone"):
        uploaded = st.file_uploader(
            "Resume file or screenshot(s)",
            type=C.RESUME_FILE_TYPES + C.RESUME_IMAGE_FILE_TYPES,
            label_visibility="collapsed",
            help=(
                "Upload one full resume file (PDF/DOCX/TXT), or one-to-"
                f"{C.MAX_RESUME_IMAGES} screenshots (PNG/JPG/WEBP) of just the "
                "sections you want parsed. Maximum 10 MB per file."
            ),
            key="resume_uploader",
            accept_multiple_files=True,
        )
    md(
        '<div class="smart-upload-note">One PDF, DOCX or TXT file — or up to '
        f'{C.MAX_RESUME_IMAGES} PNG/JPG/WEBP screenshots · maximum 10 MB per file</div>'
    )
    return uploaded or []


def _upload_and_actions() -> None:
    uploaded = _upload_widget()
    docs, images = _classify_uploads(uploaded)

    error_msg = None
    if docs and images:
        error_msg = "Upload either one resume file or screenshot(s) — not both at once."
    elif len(docs) > 1:
        error_msg = "Only one resume file can be uploaded at a time."
    elif len(images) > C.MAX_RESUME_IMAGES:
        error_msg = f"Upload at most {C.MAX_RESUME_IMAGES} screenshots at a time."

    mode = None
    if error_msg is None:
        if docs:
            mode = "file"
        elif images:
            mode = "image"
    has_upload = mode is not None

    # Upload status is rendered here — right below the uploader/help note and
    # above the action buttons — so the person can see what was detected
    # before they decide to click Parse Resume, instead of after.
    if error_msg:
        md(
            f'<div class="smart-status-row is-error">{badge("CHECK UPLOAD", "danger")} '
            f'{esc(error_msg)}</div>'
        )
    elif mode == "image":
        names = ", ".join(f.name for f in images)
        total_kb = sum(f.size for f in images) / 1024
        md(
            f'<div class="smart-status-row is-ok">{badge("UPLOADED", "accent")} '
            f'<b>{esc(names)}</b> · {total_kb:.0f} KB</div>'
        )
    elif mode == "file":
        md(
            f'<div class="smart-status-row is-ok">{badge("UPLOADED", "accent")} '
            f'<b>{esc(docs[0].name)}</b> · {docs[0].size / 1024:.0f} KB</div>'
        )
    else:
        md('<div class="smart-status-row is-neutral">No file selected</div>')

    md('<div class="smart-action-gap"></div>')

    # Narrow middle columns keep the two actions compact and centered, similar to
    # the reference composition rather than stretching them across the page.
    spacer_l, parse_col, sample_col, spacer_r = st.columns(
        [2.25, 1.35, 1.35, 2.25], gap="small"
    )
    with parse_col:
        parse = st.button(
            "Parse Resume",
            type="primary",
            use_container_width=True,
            disabled=not has_upload,
            key="parse_resume_button",
        )
    with sample_col:
        sample = st.button(
            "Load sample profile",
            use_container_width=True,
            key="load_sample_profile_button",
        )

    if parse and has_upload:
        st.session_state[C.SS_PROFILE_STATE] = "parsing"
        spinner_msg = "Parsing screenshot(s)..." if mode == "image" else "Parsing resume..."
        with st.spinner(spinner_msg):
            try:
                if mode == "image":
                    st.session_state[C.SS_PROFILE] = backend.parse_resume_image(images)
                else:
                    st.session_state[C.SS_PROFILE] = backend.parse_resume(docs[0])
                st.session_state[C.SS_PROFILE_STATE] = "ready"
                st.session_state[C.SS_JOB_RESULTS] = None
                st.session_state[C.SS_TARGET_JOB] = None
                st.session_state[C.SS_CV_RESULT] = None
                st.session_state[C.SS_CHAT] = []
            except backend.BackendError as exc:
                st.session_state[C.SS_PROFILE_STATE] = "error"
                st.session_state["profile_error"] = str(exc)
        st.rerun()

    if sample:
        with st.spinner("Building candidate profile..."):
            try:
                st.session_state[C.SS_PROFILE] = backend.parse_resume(None, demo=True)
                st.session_state[C.SS_PROFILE_STATE] = "ready"
                st.session_state[C.SS_JOB_RESULTS] = None
                st.session_state[C.SS_TARGET_JOB] = None
                st.session_state[C.SS_CV_RESULT] = None
                st.session_state[C.SS_CHAT] = []
            except backend.BackendError as exc:
                st.session_state[C.SS_PROFILE_STATE] = "error"
                st.session_state["profile_error"] = str(exc)
        st.rerun()


def _profile_card(p: dict) -> None:
    is_sample = p.get("source") == "sample"
    label = sample_badge("SAMPLE PROFILE") if is_sample else badge("Successfully parsed", "accent")
    checks = "".join(
        f'<li><span class="c {"" if ok else "off"}">✓</span>{esc(t)}</li>'
        for t, ok in p.get("completeness_items", [])
    )
    skills_preview = chips(p.get("skills", [])[:12])
    md(
        '<div class="profile-card">'
        f'<div class="sh-card-title"><span class="left">Candidate Profile {label}</span></div>'
        '<div class="profile-layout">'
        '<div class="profile-main">'
        f'<div class="sh-avatar-lg">{esc(p["initial"])}</div>'
        '<div class="profile-text">'
        f'<div class="profile-name">{esc(p["name"])}</div>'
        + (
            f'<div class="profile-role">{esc(p["target_role"])}'
            f'<span class="profile-role-tag">stated on resume</span></div>'
            if p["target_role"] else ''
        ) +
        f'<div class="sh-kv">{esc(p["location"])}</div>'
        f'<div class="sh-kv">{esc(p["email"])}</div>'
        f'<div class="sh-kv">{p["experience_years"]} years experience · {esc(p["education"])}</div>'
        f'<div class="profile-skills">{skills_preview}</div>'
        '</div></div>'
        '<div class="profile-checks">'
        '<div class="profile-check-title">Profile fields</div>'
        f'<ul class="check-list">{checks}</ul>'
        '</div></div></div>'
    )


def _profile_tabs(p: dict) -> None:
    tabs = st.tabs(["Skills", "Experience", "Education", "Projects", "Certifications", "Summary"])
    with tabs[0]:
        md(f'<div class="tab-panel">{chips(p["skills"])}</div>')
    with tabs[1]:
        for e in p["experience"]:
            pts = "".join(f"<li>{esc(x)}</li>" for x in e["points"])
            md(
                f'<div class="sub-card"><div class="sub-card-head"><b>{esc(e["title"])}</b>'
                f'<span class="badge neutral">{esc(e["period"])}</span></div>'
                f'<div class="sub-card-meta">{esc(e["company"])}</div>'
                f'<ul class="sub-list">{pts}</ul></div>'
            )
    with tabs[2]:
        for ed in p["education_items"]:
            md(
                f'<div class="sub-card"><b>{esc(ed["degree"])}</b>'
                f'<div class="sub-card-meta">{esc(ed["school"])} · {esc(ed["period"])}</div>'
                f'<div class="sub-card-muted">{esc(ed["detail"])}</div></div>'
            )
    with tabs[3]:
        cols = st.columns(2, gap="small")
        for i, pr in enumerate(p["projects"]):
            with cols[i % 2]:
                md(
                    f'<div class="sub-card project-card"><b>{esc(pr["name"])}</b>'
                    f'<p>{esc(pr["description"])}</p>{chips(pr["tech"], "neutral")}</div>'
                )
    with tabs[4]:
        certifications = p.get("certifications", []) or []
        achievements = p.get("achievements", []) or []
        if not certifications and not achievements:
            md('<div class="tab-panel"><span class="body-copy">No certifications or achievements were found on this resume.</span></div>')
        if certifications:
            md('<div class="sub-card-head"><b>Certifications</b></div>')
            for c in certifications:
                meta = " · ".join(x for x in [c.get("issuer", ""), c.get("year", "")] if x)
                md(
                    f'<div class="sub-card"><b>{esc(c.get("name", ""))}</b>'
                    + (f'<div class="sub-card-meta">{esc(meta)}</div>' if meta else '')
                    + '</div>'
                )
        if achievements:
            md('<div class="sub-card-head" style="margin-top:.6rem"><b>Achievements & Honors</b></div>')
            pts = "".join(f"<li>{esc(x)}</li>" for x in achievements)
            md(f'<div class="sub-card"><ul class="sub-list">{pts}</ul></div>')
    with tabs[5]:
        md(f'<div class="summary-panel">{esc(p["summary"])}</div>')


def render() -> None:
    _front_page_styles()
    _project_banner()
    _page_intro()
    _upload_and_actions()

    profile_state = st.session_state[C.SS_PROFILE_STATE]
    profile = state.profile()

    if profile_state == "error":
        error_state("Unable to parse this document.", st.session_state.get("profile_error", ""))

    if profile:
        try:
            _profile_card(profile)
            _profile_tabs(profile)
        except Exception:
            # A profile stored in this browser session before the shape fix
            # (or otherwise malformed) can no longer be rendered safely. Rather
            # than crash the whole page on every rerun, clear it and ask for a
            # fresh parse instead of leaving a permanently broken session.
            state.clear_profile()
            error_state(
                "The saved profile was in an old/incomplete format and could not be displayed.",
                "It has been cleared automatically — please upload and parse your resume again.",
            )
            return

        # Deliberate whitespace before the next-page action so the button does not
        # touch the preceding profile/tabs card.
        st.markdown('<div style="height: 1.1rem;"></div>', unsafe_allow_html=True)
        left_space, action = st.columns([4.8, 1.55], gap="small")
        with action:
            if st.button(
                "Next: View Matching Jobs →",
                type="primary",
                use_container_width=True,
                key="resume_next_jobs",
            ):
                state.go_to(C.PAGE_JOBS)
                st.rerun()
    else:
        empty_state(
            "No resume analyzed yet",
            "Upload a resume to build your candidate profile.",
            icon="doc",
        )