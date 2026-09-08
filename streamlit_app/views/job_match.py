from __future__ import annotations

import streamlit as st

from .. import backend, config as C, state
from ..components import chips, empty_state, error_state, esc, md, metric_row, page_header, score_pill


CUSTOM_OPTION = "Custom search..."
COMMON_ROLE_OPTIONS = [
    "UI/UX Designer", "UI/UX Design Engineer", "UI/UX Developer", "UX Designer",
    "Product Designer", "Software Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Data Scientist", "Machine Learning Engineer", "Data Analyst",
    "Business Analyst", "DevOps Engineer", "Cloud Engineer", "Python Developer",
    "Java Developer", "React Developer", "QA Engineer", "Cybersecurity Analyst",
]

JOB_MATCH_PAGE_CSS = """
<style>
.jd-card-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:15px;
  font-weight:600;
  margin-bottom:.25rem;
}
.jd-card-sub, .job-description-copy{
  color:var(--muted);
  font-size:12.5px;
  line-height:1.55;
  margin-bottom:.7rem;
}

/* JD input box: targeted by its own st.container key.
   IMPORTANT: the installed Streamlit build (1.63) no longer renders a
   [data-testid="stVerticalBlockBorderWrapper"] element at all -- that
   wrapper testid was removed in a frontend refactor. A `key=` on
   st.container() is still added as a plain CSS class ("st-key-<key>")
   directly on the [data-testid="stVerticalBlock"] element itself, so
   that's what we target. This is why the card kept showing the peach
   page background before: every rule guarded by the old testid was
   silently matching nothing. */
.st-key-jd_card{
  background:#FFFFFF !important;
  border:1px solid #171B2B !important;
  border-radius:16px !important;
  box-shadow:0 1px 2px rgba(20,20,40,.04), 0 8px 22px -14px rgba(20,20,40,.14) !important;
  padding:1.05rem 1.05rem !important;
}
.st-key-jd_card > div{
  background:#FFFFFF !important;
  border-radius:15px !important;
}
.st-key-jd_card .stElementContainer{
  margin-top:0 !important;
  margin-bottom:0 !important;
}
.st-key-jd_card [data-testid="stForm"]{
  border:none !important;
  padding:0 !important;
  margin:0 !important;
  background:transparent !important;
}

/*
  The Send button is deliberately overlaid on the textarea itself.
  The form is the positioning context; the submit-button wrapper is removed
  from normal flow so it cannot create a second row or drift to the left.
*/
.st-key-jd_input_wrap{
  position:relative !important;
  width:100% !important;
  margin:0 !important;
  padding:0 !important;
}
.st-key-jd_input_wrap [data-testid="stForm"]{
  position:relative !important;
  width:100% !important;
  min-height:150px !important;
}
.st-key-jd_input_wrap [data-testid="stTextArea"]{
  width:100% !important;
  margin:0 !important;
}
.st-key-jd_input_wrap [data-testid="stTextArea"] textarea{
  width:100% !important;
  min-height:150px !important;
  padding:.75rem 5.6rem 3.15rem .85rem !important;
}
.st-key-jd_input_wrap [data-testid="stFormSubmitButton"]{
  position:absolute !important;
  right:.75rem !important;
  bottom:.75rem !important;
  width:auto !important;
  margin:0 !important;
  padding:0 !important;
  z-index:20 !important;
  display:block !important;
  pointer-events:none !important;
}
.st-key-jd_input_wrap [data-testid="stFormSubmitButton"] button{
  pointer-events:auto !important;
  width:auto !important;
  min-width:62px !important;
  height:32px !important;
  min-height:32px !important;
  padding:.25rem .95rem !important;
  margin:0 !important;
  border-radius:999px !important;
  font-size:12.5px !important;
  font-weight:600 !important;
  white-space:nowrap !important;
  background:var(--accent) !important;
  border:1px solid var(--accent) !important;
  color:#FFFFFF !important;
  box-shadow:0 3px 10px -3px rgba(79,70,229,.45) !important;
}
.st-key-jd_input_wrap [data-testid="stFormSubmitButton"] button:hover{
  background:#4338CA !important;
  border-color:#4338CA !important;
  color:#FFFFFF !important;
}
/* JD input + the search row's fields: same light gray-blue as the resume
   uploader box on the Resume Analysis page (#F1F3F7), so every "input
   surface" across the app reads consistently. */
[data-testid="stTextArea"] textarea{
  background:#F1F3F7 !important;
  border:1px solid #171B2B !important;
  border-radius:12px !important;
  box-shadow:none !important;
}
[data-testid="stTextArea"] textarea:focus{
  border-color:var(--accent) !important;
  box-shadow:0 0 0 3px rgba(79,70,229,.12) !important;
}

.job-search-row [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.job-search-row [data-testid="stTextInput"] input{
  background:#F1F3F7 !important;
  border:1px solid #171B2B !important;
}
.job-search-row .stButton > button{ min-height:44px !important; }

/* The expandable "View Details" panel under a job card is also an inner
   surface - same treatment. */
.job-details{ background:#F1F3F7 !important; }

/* Final JD Send-button refinement: stable keyed widget, white text, slightly
   inset from the bottom-right corner of the textarea. */
.st-key-jd_card .st-key-jd_send{
  position:absolute !important;
  right:1.05rem !important;
  bottom:1.00rem !important;
  width:auto !important;
  margin:0 !important;
  padding:0 !important;
  z-index:100 !important;
}
.st-key-jd_card .st-key-jd_send button,
.st-key-jd_card .st-key-jd_send button p,
.st-key-jd_card .st-key-jd_send button span,
.st-key-jd_card .st-key-jd_send button div{
  color:#FFFFFF !important;
}
.st-key-jd_card .st-key-jd_send button{
  min-width:62px !important;
  height:32px !important;
  min-height:32px !important;
  padding:.25rem .9rem !important;
  background:var(--accent) !important;
  border:1px solid var(--accent) !important;
  border-radius:999px !important;
  box-shadow:0 3px 10px -3px rgba(79,70,229,.45) !important;
}
.st-key-jd_card .st-key-jd_send button:hover{
  color:#FFFFFF !important;
  background:#4338CA !important;
  border-color:#4338CA !important;
}

</style>
"""

def _run_search(query: str) -> None:
    query = (query or "").strip()
    if not query:
        return
    st.session_state[C.SS_JOB_QUERY] = query
    st.session_state[C.SS_JOB_STATE] = "searching"
    with st.spinner("Searching jobs..."):
        try:
            result = backend.search_jobs(query, state.profile())
        except backend.BackendError as exc:
            st.session_state[C.SS_JOB_STATE] = "error"
            st.session_state["job_error"] = str(exc)
            return
    st.session_state[C.SS_JOB_RESULTS] = result
    st.session_state[C.SS_JOB_STATE] = "ready" if result.get("jobs") else "empty"


def _autocomplete_options() -> list[str]:
    titles: list[str] = []
    try:
        from src.data.loader import load_jobs
        seen: set[str] = set()
        for job in load_jobs()[:1000]:
            title = (job.title or "").strip()
            if title and title.casefold() not in seen:
                seen.add(title.casefold())
                titles.append(title)
    except Exception:
        titles = []

    ordered: list[str] = []
    seen: set[str] = set()
    for item in [*COMMON_ROLE_OPTIONS, *titles]:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            ordered.append(item)
    return ordered + [CUSTOM_OPTION]


def _save_job_description() -> bool:
    """Persist the pasted JD and turn it into a target job for CV Improvement.

    Returns True if there was actually a job description to act on.
    """
    text = (st.session_state.get("job_description_input", "") or "").strip()
    st.session_state[C.SS_JOB_DESCRIPTION] = text
    if not text:
        return False
    # Pull a short title from the first non-empty line for the "Target Job"
    # card on CV Improvement; the full pasted text still goes to the LLM as
    # the job description so nothing is lost.
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "Pasted Job Description")
    st.session_state[C.SS_TARGET_JOB] = {
        "title": first_line[:80],
        "company": "",
        "location": "",
        "description": text,
        "skills": "",
    }
    st.session_state[C.SS_CV_RESULT] = None
    return True


def _job_description_input() -> None:
    """Capture a pasted JD and jump straight to CV Improvement with it.

    The textarea + a small "Send" button live inside an st.form (so Enter
    also submits). The button is pulled up over the textarea's bottom-right
    corner with a negative margin (see `.st-key-jd_input_wrap` in
    JOB_MATCH_PAGE_CSS above) so it reads as part of the input instead of a
    separate row underneath it.
    """
    with st.container(border=True, key="jd_card"):
        md('<div class="jd-card-title">Paste a Job Description</div>')
        md(
            '<div class="job-description-copy">'
            'You can either paste a job opening description here and hit Send, or search the job corpus below. '
            'Use either route to find or target a job for CV Improvement.'
            '</div>'
        )
        with st.container(key="jd_input_wrap"):
            with st.form("jd_form", border=False, clear_on_submit=False):
                st.text_area(
                    "Job description",
                    value=st.session_state.get(C.SS_JOB_DESCRIPTION, ""),
                    placeholder="Paste the full job description here...",
                    height=150,
                    label_visibility="collapsed",
                    key="job_description_input",
                )
                submitted = st.form_submit_button("Send", type="primary", key="jd_send")
    if submitted:
        if _save_job_description():
            state.go_to(C.PAGE_CV)
            st.rerun()
        else:
            st.warning("Paste a job description first.")
    st.markdown('<div style="height:.9rem"></div>', unsafe_allow_html=True)

def _search_bar() -> None:
    st.markdown(
        '<div class="search-help">Search a role, skill, or keyword. Start typing to see matching suggestions.</div>',
        unsafe_allow_html=True,
    )
    options = _autocomplete_options()
    c1, c2 = st.columns([5, 1], gap="small", vertical_alignment="bottom")
    with c1:
        selected = st.selectbox(
            "Search for jobs",
            options,
            index=None,
            placeholder="Search for job titles, skills or keywords...",
            label_visibility="collapsed",
            key="job_role_autocomplete",
        )
        query = selected or ""
        if selected == CUSTOM_OPTION:
            query = st.text_input(
                "Custom job query",
                placeholder="Type any role, skill, or keyword...",
                label_visibility="collapsed",
                key="custom_job_query",
            )
    with c2:
        go = st.button("Search", type="primary", use_container_width=True, key="job_search_button")

    if go and query.strip():
        _run_search(query)
        st.rerun()


def _suggested_roles() -> None:
    roles = backend.suggest_roles(state.profile())
    md(
        '<div class="section-head"><span>Suggested Roles '
        '<span class="section-note">Ranked from your profile and the job corpus</span></span>'
        '<span class="badge good">PROFILE RANKING</span></div>'
    )
    cols = st.columns(3, gap="small")
    for rank, (col, r) in enumerate(zip(cols, roles), start=1):
        with col:
            md(
                f'<div class="role-card rank-{rank}">'
                f'<div class="role-rank">#{rank}</div><div class="ico">💼</div><div class="role-body">'
                f'<div class="n">{esc(r["role"])}</div>'
                f'<div class="j">{r["jobs"]:,} relevant jobs in the corpus</div>'
                f'<div class="r">{esc(r["reason"])}</div></div></div>'
            )
            if st.button(
                f"Search {r['role']}",
                key=f"role_{r['role']}",
                use_container_width=True,
            ):
                _run_search(r["role"])
                st.rerun()


def _job_card(rank: int, j: dict) -> None:
    matching = chips(j.get("matching", []), "good") if j.get("matching") else ""
    missing = (
        f'<div class="job-missing">Missing: {chips(j["missing"], "warn")}</div>'
        if j.get("missing") else ""
    )
    details_key = f"view_{j.get('job_id', rank)}"
    target_key = f"target_{j.get('job_id', rank)}"
    detail_open = st.session_state.get("job_detail") == details_key

    card_class = "job-card top" if rank == 1 else "job-card"
    md(
        f'<div class="{card_class}">'
        f'<div class="job-card-grid"><div class="job-rank">{rank:02d}</div>'
        '<div class="job-content">'
        f'<div class="job-title">{esc(j["title"])}</div>'
        f'<div class="job-meta"><b>{esc(j["company"])}</b> · {esc(j["location"])} · {esc(j["mode"])} · {esc(j["type"])} · {esc(j["posted"])}</div>'
        f'<div class="job-chips">{matching}</div>{missing}'
        f'<div class="job-why">{esc(j["why"])}</div>'
        '</div><div class="job-score">'
        f'{score_pill(j["score"])}'
        '</div></div></div>'
    )
    a, b = st.columns([1, 1], gap="small")
    with a:
        if st.button("View Details", key=details_key, use_container_width=True):
            st.session_state["job_detail"] = details_key if not detail_open else None
            st.rerun()
    with b:
        if st.button(
            "Target this job →",
            key=target_key,
            type="primary",
            use_container_width=True,
        ):
            st.session_state[C.SS_TARGET_JOB] = {**j}
            st.session_state[C.SS_CV_RESULT] = None
            state.go_to(C.PAGE_CV)
            st.rerun()

    if detail_open:
        md(
            f'<div class="job-details"><div><b>Role:</b> {esc(j["title"])}</div>'
            f'<div><b>Experience:</b> {esc(j.get("experience", "Not specified"))}</div>'
            f'<div><b>Match:</b> {j["score"]}%</div>'
            f'<p>{esc(j.get("description", ""))}</p>'
            f'<div><b>Skills:</b> {esc(j.get("skills", "") or "Not specified")}</div>'
            + (
                f'<a href="{esc(j["url"])}" target="_blank">Open source listing ↗</a>'
                if j.get("url") else ""
            )
            + '</div>'
        )


def _results() -> None:
    state_name = st.session_state[C.SS_JOB_STATE]
    res = st.session_state[C.SS_JOB_RESULTS]
    if state_name == "error":
        error_state("Search failed.", st.session_state.get("job_error", "Please try again."))
        return
    if state_name == "empty":
        empty_state("No matching jobs were found.", "Try a broader title or remove some keywords.", icon="search")
        return
    if not res:
        empty_state(
            "Search for a role to see matching jobs.",
            "Choose a suggested role above or start typing in the role search.",
            icon="search",
        )
        return

    s = res["summary"]
    md(
        '<div class="section-head results-head"><span>Match Summary</span>'
        '<span class="badge accent">SEMANTIC SEARCH</span></div>'
    )
    metric_row([
        ("Relevant Jobs", s["relevant_jobs"], "for this query", ""),
        ("Best Match", s["best_match"], "top ranked role", "good"),
        ("Average Match", s["avg_match"], "across results", "accent"),
    ])

    query = esc(st.session_state[C.SS_JOB_QUERY] or "your query")
    md(
        '<div class="section-head jobs-head"><span>Top Matching Jobs '
        f'<span class="section-note">for "{query}" · ranked best → least match</span></span>'
        '<span class="badge neutral">Sorted by match score</span></div>'
    )
    for i, job in enumerate(res["jobs"], start=1):
        _job_card(i, job)

    if res.get("jobs"):
        spacer, action = st.columns([4.2, 1.3], gap="small")
        with action:
            if st.button(
                "Next: CV Improvement →",
                type="primary",
                use_container_width=True,
                key="jobs_next_cv",
            ):
                best = res["jobs"][0]
                st.session_state[C.SS_TARGET_JOB] = {**best}
                st.session_state[C.SS_CV_RESULT] = None
                state.go_to(C.PAGE_CV)
                st.rerun()


def render() -> None:
    st.markdown(JOB_MATCH_PAGE_CSS, unsafe_allow_html=True)
    page_header(
        "Job Match",
        "Job Match",
        "Find opportunities that match your skills, experience and career direction.",
    )
    _job_description_input()
    _search_bar()
    _suggested_roles()
    _results()