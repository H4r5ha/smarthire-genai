from __future__ import annotations

import streamlit as st

from .. import backend, config as C, state
from ..components import chips, empty_state, error_state, esc, md, metric_row, page_header, score_pill


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

/* Role/keyword search box: same white card treatment as the "Paste a Job
   Description" card above it, so the two entry points read as matching
   halves of one row instead of one styled card next to bare, unstyled
   widgets. */
.st-key-search_card{
  background:#FFFFFF !important;
  border:1px solid #171B2B !important;
  border-radius:16px !important;
  box-shadow:0 1px 2px rgba(20,20,40,.04), 0 8px 22px -14px rgba(20,20,40,.14) !important;
  padding:1.05rem 1.05rem !important;
}
.st-key-search_card > div{
  background:#FFFFFF !important;
  border-radius:15px !important;
}
.st-key-search_card .stElementContainer{
  margin-top:0 !important;
  margin-bottom:0 !important;
}
/* Selectbox + custom-search text input: same shaded input surface used by
   the JD textarea and the resume uploader (#F1F3F7), instead of the
   previous `.job-search-row` selector, which was never attached to any
   actual element and so never matched anything.

   The selectbox itself needs several selector shapes, not just one: an
   app-wide rule in styles.py ([data-testid="stSelectbox"] > div > div)
   already forces a plain white background with !important, and it can
   land on a different nested div than [data-baseweb="select"] > div
   depending on the installed Streamlit build. Rather than guess which
   node is the "real" visible one, every plausible candidate is covered
   here -- each scoped under .st-key-search_card, which outranks the
   unscoped global rule on specificity regardless of which one actually
   paints the pixel. */
.st-key-search_card [data-testid="stSelectbox"] > div > div,
.st-key-search_card [data-testid="stSelectbox"] [data-baseweb="select"],
.st-key-search_card [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.st-key-search_card [data-testid="stSelectbox"] [data-baseweb="select"] div[role="combobox"],
.st-key-search_card [data-testid="stTextInput"] input{
  background:#F1F3F7 !important;
  border:1px solid #171B2B !important;
  border-radius:12px !important;
  box-shadow:none !important;
}
.st-key-search_card [data-testid="stSelectbox"]:focus-within > div > div,
.st-key-search_card [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
.st-key-search_card [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div,
.st-key-search_card [data-testid="stTextInput"] input:focus{
  border-color:var(--accent) !important;
  box-shadow:0 0 0 3px rgba(79,70,229,.12) !important;
}
.st-key-search_card .stButton > button{ min-height:44px !important; }
/* The search box now wraps its selectbox + button in an st.form so pressing
   Enter submits the search (a bare selectbox + a separate st.button outside
   any form never responds to Enter). The form adds its own default border
   and padding, which must be stripped so the card keeps looking like one
   surface, and the submit button needs the same primary-blue treatment as
   every other .stButton since [data-testid="stFormSubmitButton"] is a
   different element and isn't covered by the app's .stButton rules. */
.st-key-search_card [data-testid="stForm"]{
  border:none !important;
  padding:0 !important;
  margin:0 !important;
  background:transparent !important;
}
.st-key-search_card [data-testid="stFormSubmitButton"] button{ min-height:44px !important; }
.st-key-search_card [data-testid="stFormSubmitButton"] button[kind="primary"]{
  background:var(--accent) !important;
  border-color:var(--accent) !important;
  color:#fff !important;
  box-shadow:0 8px 18px -10px rgba(79,70,229,.7) !important;
}
.st-key-search_card [data-testid="stFormSubmitButton"] button[kind="primary"]:hover{
  background:#4338CA !important;
  border-color:#4338CA !important;
}
.st-key-search_card [data-testid="stFormSubmitButton"] button[kind="primary"] *{
  color:#fff !important;
}

/* The expandable "View Details" panel under a job card is also an inner
   surface - same treatment. */
.job-details{ background:#F1F3F7 !important; }

/* ---------- Top "three ways in" intro card ---------- */
.jm-intro{
  margin:0 0 1.3rem 0;
  padding:1.1rem 1.3rem 1.2rem 1.3rem;
  border-radius:var(--r-card);
  background:linear-gradient(180deg,#F5F7FF 0%,#F0F3FF 100%);
  border:1px solid var(--accent-border);
  box-shadow:var(--shadow);
}
.jm-intro-head{
  display:flex;
  align-items:center;
  gap:.55rem;
  margin-bottom:.15rem;
}
.jm-intro-ico{
  width:26px; height:26px; border-radius:8px;
  background:var(--accent); color:#fff;
  display:grid; place-items:center;
  font-size:13px; flex:none;
  box-shadow:0 4px 10px -4px rgba(79,70,229,.55);
}
.jm-intro-title{
  font-family:'Space Grotesk',sans-serif;
  font-weight:700;
  font-size:15px;
  color:var(--text);
}
.jm-intro-sub{
  color:var(--muted);
  font-size:12.5px;
  margin:0 0 .95rem 2.35rem;
}
.jm-steps{
  display:flex;
  align-items:stretch;
  gap:.9rem;
}
.jm-step{
  flex:1;
  display:flex;
  gap:.7rem;
  align-items:flex-start;
  background:#FFFFFF;
  border:1px solid var(--accent-border);
  border-radius:12px;
  padding:.75rem .85rem;
  min-width:0;
}
.jm-step-num{
  width:24px; height:24px; border-radius:50%;
  background:var(--accent-soft);
  color:var(--accent);
  border:1px solid var(--accent-border);
  font-family:'Space Grotesk',sans-serif;
  font-weight:700;
  font-size:12px;
  display:grid; place-items:center;
  flex:none;
  margin-top:1px;
}
.jm-step-body{ min-width:0; }
.jm-step-h{
  font-weight:600;
  font-size:13px;
  color:var(--text);
  line-height:1.3;
  margin-bottom:.15rem;
}
.jm-step-d{
  color:var(--muted);
  font-size:11.5px;
  line-height:1.45;
}
.jm-intro-foot{
  margin:.85rem 0 0 0;
  color:var(--muted);
  font-size:11.5px;
  font-style:italic;
}
.jm-relevance-note{
  margin:.9rem 0 1.3rem 0;
  padding:.55rem .8rem;
  border-radius:10px;
  background:var(--card-soft);
  border:1px solid var(--border);
  color:var(--muted);
  font-size:12px;
  line-height:1.5;
}
.jm-relevance-note b{ color:var(--text); }
@media (max-width: 900px){
  .jm-steps{ flex-direction:column; }
  .jm-intro-sub{ margin-left:0; }
}

/* ---------- "or" divider between the three job-targeting routes ---------- */
.or-divider{
  display:flex;
  align-items:center;
  gap:.75rem;
  margin:.15rem 0 1.1rem 0;
  color:var(--muted);
  font-size:11.5px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.09em;
}
.or-divider::before, .or-divider::after{
  content:"";
  flex:1;
  height:1px;
  background:var(--border, #E4E7EC);
}

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
    """Dropdown options for role/keyword search.

    Every entry is a title that actually exists in the job dataset -- a
    previous version merged in a fixed list of ~20 role names ahead of the
    real dataset titles, several of which (e.g. "UI/UX Designer", "DevOps
    Engineer", "QA Engineer", "Cybersecurity Analyst") have zero matching
    rows in the corpus, which made the dropdown suggest searches guaranteed
    to return an empty state.

    The widget itself is a single st.selectbox with `accept_new_options=True`
    (see `_search_bar`), which is what gives this list-plus-free-text
    behaviour: typing filters these options live as suggestions, and typing
    something that isn't in the list is still accepted and searched as-is --
    no separate "Custom search..." sentinel/escape-hatch option or second
    text field needed.
    """
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

    return sorted(titles, key=str.casefold)


def _save_job_description() -> bool:
    """Persist the pasted JD and turn it into a target job for CV Improvement.

    Returns True if there was actually a job description to act on.
    """
    text = (st.session_state.get("job_description_input", "") or "").strip()
    st.session_state[C.SS_JOB_DESCRIPTION] = text
    if not text:
        return False
    # Ask the LLM for the actual role name being advertised, reading the
    # whole pasted JD rather than just its first line -- a JD very often
    # opens with a company name, location or "We're hiring!" line before the
    # title ever appears, and that first line was previously shown verbatim
    # as the "Target Job" title regardless of whether it was a role at all.
    # If the JD genuinely states no title anywhere, this infers an
    # appropriate one from the described skills/responsibilities instead of
    # leaving the card mislabeled; it only falls back to the first line if
    # the extraction call itself fails.
    with st.spinner("Reading job description..."):
        title = backend.extract_job_title(text)
    st.session_state[C.SS_TARGET_JOB] = {
        "title": title,
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
    with st.container(border=True, key="search_card"):
        md('<div class="jd-card-title">Search a Role, Skill, or Keyword</div>')
        md(
            '<div class="jd-card-sub">Start typing to see matching suggestions from the job corpus '
            '&mdash; or keep typing your own and press Enter to search it directly.</div>'
        )
        options = _autocomplete_options()
        # Wrapped in a form so pressing Enter submits the search: a bare
        # selectbox + a separate st.button outside any form never responds
        # to the Enter key, only to an actual click.
        with st.form("job_search_form", border=False, clear_on_submit=False):
            c1, c2 = st.columns([5, 1], gap="small", vertical_alignment="bottom")
            with c1:
                selected = st.selectbox(
                    "Search for jobs",
                    options,
                    index=None,
                    placeholder="Search for job titles, skills or keywords...",
                    label_visibility="collapsed",
                    key="job_role_autocomplete",
                    accept_new_options=True,
                )
            with c2:
                go = st.form_submit_button("Search", type="primary", use_container_width=True, key="job_search_button")
        query = (selected or "").strip()

    if go and query:
        _run_search(query)
        st.rerun()


def _suggested_roles() -> None:
    try:
        roles = backend.suggest_roles(state.profile())
    except backend.BackendError as exc:
        error_state("Could not load suggested roles.", str(exc))
        return
    md(
        '<div class="section-head"><span>Suggested Roles '
        '<span class="section-note">Ranked by direct skill-fit against the job corpus '
        '&mdash; this can differ from the title on your parsed profile, which is only '
        'the role you stated on your resume, not a corpus match</span></span></div>'
    )
    if not roles:
        empty_state(
            "No resume on file yet.",
            "Upload or paste your resume on the Resume Analysis page to see roles "
            "matched to your actual skills, or use the job description box or "
            "role dropdown above to search right away.",
            icon="user",
        )
        return
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
    personalized = s.get("personalized", False)
    if personalized:
        md(
            '<div class="section-head results-head"><span>Match Summary</span>'
            '<span class="badge accent">SEMANTIC SEARCH</span></div>'
        )
        metric_row([
            ("Relevant Jobs", s["relevant_jobs"], "for this query", ""),
            ("Best Match", s["best_match"], "top ranked role", "good"),
            ("Average Match", s["avg_match"], "across results", "accent"),
        ])
    else:
        # No resume on file: the percentages below are query/role-to-job
        # semantic relevance, not a personalized fit score, so they must not
        # be labeled "Match" -- that implies scored against the candidate,
        # which there isn't one for yet.
        md(
            '<div class="section-head results-head"><span>Search Relevance</span>'
            '<span class="badge neutral">KEYWORD SEARCH \u2014 NO RESUME</span></div>'
        )
        metric_row([
            ("Relevant Jobs", s["relevant_jobs"], "for this query", ""),
            ("Best Relevance", s["best_match"], "top ranked job", ""),
            ("Average Relevance", s["avg_match"], "across results", ""),
        ])
        md(
            '<div class="jm-relevance-note">Upload your resume on the Resume Analysis '
            'page to see a personalized <b>Match</b> score instead of plain search relevance.</div>'
        )

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


def _or_divider() -> None:
    md('<div class="or-divider"><span>or</span></div>')


def render() -> None:
    st.markdown(JOB_MATCH_PAGE_CSS, unsafe_allow_html=True)
    page_header(
        "Job Match",
        "Job Match",
        "Find opportunities that match your skills, experience and career direction.",
    )
    md(
        '<div class="jm-intro">'
        '<div class="jm-intro-head">'
        '<div class="jm-intro-ico">&#9889;</div>'
        '<div class="jm-intro-title">Three ways to find your target job</div>'
        '</div>'
        '<div class="jm-intro-sub">Pick whichever is fastest &mdash; each path leads to the same matched results.</div>'
        '<div class="jm-steps">'
        '<div class="jm-step"><div class="jm-step-num">1</div>'
        '<div class="jm-step-body"><div class="jm-step-h">Paste a job description</div>'
        '<div class="jm-step-d">Drop in any JD below and we\'ll score your fit against it.</div></div></div>'
        '<div class="jm-step"><div class="jm-step-num">2</div>'
        '<div class="jm-step-body"><div class="jm-step-h">Search or pick a role</div>'
        '<div class="jm-step-d">Type a title into the dropdown to search the job corpus.</div></div></div>'
        '<div class="jm-step"><div class="jm-step-num">3</div>'
        '<div class="jm-step-body"><div class="jm-step-h">Choose a suggested role</div>'
        '<div class="jm-step-d">Jump straight to one of your top 3 profile-based matches.</div></div></div>'
        '</div>'
        '</div>'
    )
    _job_description_input()
    _or_divider()
    _search_bar()
    _or_divider()
    _suggested_roles()
    _results()