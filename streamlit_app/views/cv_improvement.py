"""Page 3 - CV Improvement."""
from __future__ import annotations

import streamlit as st

from .. import backend, config as C, sample_data as sd, state
from ..components import badge, chip, empty_state, esc, md, page_header, ring, sample_badge


CV_PAGE_CSS = """
<style>
/* ===================================================================
   Why this file targets containers by `key=` instead of the generic
   [data-testid="stVerticalBlockBorderWrapper"] selector:

   That testid doesn't exist at all in the installed Streamlit build
   (1.63) -- it was removed in a frontend refactor, so every rule that
   was gated on it (including an earlier version of this very file)
   was matching zero elements, which is why the cards kept showing the
   peach page background instead of white. In this build, `key=` on
   st.container() is added as a plain CSS class ("st-key-<key>")
   directly on the [data-testid="stVerticalBlock"] element itself.
   Every container below has a unique `key="cv_card_*"`, so we select
   on that class directly (scoped, guaranteed unique to these boxes)
   instead of depending on an internal testid that can change again.
   ===================================================================*/
[class*="st-key-cv_card_"]{
  background-color:#FFFFFF !important;
  border:1px solid #171B2B !important;
  border-radius:16px !important;
  padding-top:1.15rem !important;
  padding-bottom:1.15rem !important;
  padding-left:1.2rem !important;
  padding-right:1.2rem !important;
  box-sizing:border-box !important;
  gap:.68rem !important;
  box-shadow:0 6px 20px -12px rgba(20,20,40,.18), 0 2px 6px rgba(20,20,40,.06) !important;
}
[class*="st-key-cv_card_"] .stElementContainer{
  margin:0 !important;
}
.cv-card-edge-space{
  display:block;
  flex:0 0 .55rem;
  height:.55rem;
  min-height:.55rem;
  width:100%;
  margin:0 !important;
  padding:0 !important;
}
[class*="st-key-cv_card_"] [data-testid="stVerticalBlock"]{
  gap:.6rem !important;
}
[class*="st-key-cv_card_"] *{
  box-sizing:border-box;
}
[data-testid="column"]{ min-width:0 !important; }

.sh-metric,
.summary-box,
.ba-card,
.why-box,
.issue-row,
.rec{
  background:#F1F3F7 !important;
  border:1px solid #171B2B !important;
  box-shadow:none !important;
}

.cv-gap{ height:.9rem; }

.card-heading{
  margin-bottom:.85rem !important;
}

.readiness-body{
  display:flex;
  align-items:center;
  gap:1.2rem;
}

.score-compare{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:1.4rem;
  flex-wrap:wrap;
}

.score-block{
  text-align:center;
}

.score-block .score-label{
  font-size:11px;
  letter-spacing:.08em;
  text-transform:uppercase;
  color:var(--muted);
  font-weight:600;
  margin-top:.5rem;
}

.score-arrow{
  font-size:22px;
  color:var(--accent);
  font-weight:600;
}

.readiness-copy,
.body-copy{
  color:var(--muted);
  font-size:13px;
  line-height:1.65;
}

/* Missing Technical Skills: each priority level is its own labeled,
   colour-tinted block, with the badge, arrow, and its chips all on one
   wrapping line -- so High / Medium / Low read as distinct groups without
   splitting the label from its own chips onto separate lines. */
.priority-group{
  border-left:3px solid var(--border);
  background:#FAFAF8;
  border-radius:10px;
  padding:.55rem .85rem;
  margin:.55rem 0;
}
.priority-group.high{ border-left-color:#E2897B; background:#FDF4F2; }
.priority-group.medium{ border-left-color:#E7C26E; background:#FBF6E9; }
.priority-group.neutral{ border-left-color:#C7CCD6; background:#F5F5F2; }

.priority-group-row{
  display:flex;
  flex-wrap:wrap;
  align-items:center;
  gap:.45rem;
}
.priority-arrow{
  color:var(--accent);
  font-weight:700;
  font-size:13px;
  opacity:.75;
  margin-right:.05rem;
}

.summary-box{
  padding:.9rem 1rem !important;
  font-size:13.5px;
  line-height:1.7;
}

.summary-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) 115px;
  gap:.8rem;
  align-items:start;
}

.summary-copy-button .stButton > button{
  margin-top:0 !important;
}

.rewrite-row{
  display:grid;
  grid-template-columns:28px minmax(0,1fr);
  gap:.75rem;
  margin:.8rem 0 1rem;
}

.rewrite-index{
  width:28px;
  height:28px;
  border-radius:9px;
  background:var(--accent-soft);
  color:var(--accent);
  display:grid;
  place-items:center;
  font-size:12px;
  font-weight:700;
}

.rewrite-title{
  font-family:'Space Grotesk',sans-serif;
  font-weight:600;
  font-size:14px;
  margin-bottom:.5rem;
}

.rewrite-grid{
  display:grid;
  grid-template-columns:1fr;
  gap:.7rem;
}

.ba-card{
  padding:.9rem 1rem !important;
  min-height:0 !important;
  height:auto !important;
  border-radius:14px !important;
}

.ba-card .lbl{
  font-size:10.5px;
  letter-spacing:.14em;
  font-weight:600;
  color:var(--muted);
  margin-bottom:.4rem;
}

.ba-card.after .lbl{
  color:var(--success);
}

.ba-card.after{
  background:var(--success-soft) !important;
  border-color:#BFE6D1 !important;
}

.ba-card .txt{
  font-size:13.5px;
  line-height:1.6;
}

.why-box{
  padding:.6rem .8rem !important;
  margin:.65rem 0 0 !important;
}

.skills-followup{
  margin-top:.65rem;
}

.issue-row{
  display:grid;
  grid-template-columns:auto minmax(0,1fr);
  gap:.55rem;
  align-items:start;
  margin:.6rem 0;
  padding:.65rem .75rem !important;
  border-radius:12px !important;
}

.issue-copy{
  color:var(--muted);
  font-size:12.5px;
  line-height:1.55;
}

.issue-copy b{
  color:var(--text);
  display:block;
  margin-bottom:.18rem;
}

.rec{
  display:flex;
  gap:.9rem;
  align-items:flex-start;
  padding:.85rem 1rem !important;
  margin-bottom:.6rem;
  border-radius:12px !important;
}

.next-action-gap{ height:1rem; }

@media(max-width:900px){
  .summary-row{ grid-template-columns:1fr; }
}
</style>
"""


def _gap() -> None:
    st.markdown('<div class="cv-gap"></div>', unsafe_allow_html=True)


def _card_edge_bottom() -> None:
    """Render the retained bottom breathing room inside each CV card."""
    st.markdown(
        '<div class="cv-card-edge-space" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )


def _target_job_card(job: dict) -> None:
    with st.container(border=True, key="cv_card_target_job"):
        left, right = st.columns([5.2, 1.1], gap="medium", vertical_alignment="center")
        with left:
            md(
                '<div class="eyebrow">TARGET JOB</div>'
                f'<div class="target-title">{esc(job.get("title", "Untitled role"))}</div>'
                f'<div class="target-meta"><b>{esc(job.get("company", "Unknown company"))}</b> · {esc(job.get("location", "Not specified"))}</div>'
            )
        with right:
            if st.button("Change Job", type="primary", use_container_width=True, key="cv_change_job"):
                state.go_to(C.PAGE_JOBS)
                st.rerun()
        _card_edge_bottom()


def _readiness_tone(percent: int) -> str:
    """Ring colour follows the same score it's drawn from, using the app's
    existing green/blue/amber palette (no new colours introduced)."""
    if percent >= 70:
        return ""       # default green (var(--success))
    if percent >= 40:
        return "accent"  # blue
    return "warn"        # amber


def _ats_score(r: dict) -> None:
    """The headline number: a Before score (today's resume, as-is) and an
    After score (what the free rewrites on this page alone could realistically
    buy back, before learning anything new) — both derived from the same
    matched/missing evidence shown in the cards right below, so they can never
    contradict each other."""
    matched_count = int(r.get("matched", len(r.get("matched_skills", []) or [])))
    missing_count = int(r.get("missing_count", 0))
    total = matched_count + missing_count
    before = int(r.get("ats_score_before", r.get("readiness", 0)))
    after = int(r.get("ats_score_after", before))

    with st.container(border=True, key="cv_card_ats_score"):
        md('<div class="card-heading">ATS Match Score</div>')
        md(
            '<div class="score-compare">'
            f'<div class="score-block">{ring(before, tone=_readiness_tone(before), size="sm")}'
            '<div class="score-label">Before</div></div>'
            '<div class="score-arrow">→</div>'
            f'<div class="score-block">{ring(after, tone=_readiness_tone(after), size="sm")}'
            '<div class="score-label">After free edits</div></div>'
            '</div>'
        )
        if total > 0:
            copy = (
                f'This role\u2019s description lists <b>{total}</b> concrete requirements. Your resume '
                f'currently matches <b>{matched_count}</b> of them — the <b>{before}%</b> score on the '
                'left. Applying the rewrites and additions on this page (no new skills needed yet) could '
                f'realistically raise that to about <b>{after}%</b> — closing the rest means learning the '
                'missing skills below.'
            )
        else:
            copy = (
                'No explicit target-role requirements could be extracted, so these scores reflect an '
                'overall profile read rather than a skill-by-skill count.'
            )
        md(f'<div class="body-copy" style="margin-top:.9rem">{copy}</div>')
        _card_edge_bottom()


def _matched_skills(r: dict) -> None:
    """Skills already on the resume that are pulling the score up."""
    matched = list(r.get("matched_skills", []) or [])
    with st.container(border=True, key="cv_card_matched_skills"):
        md('<div class="card-heading">Skills Already Working For You</div>')
        if matched:
            md(
                '<div class="body-copy">These already appear on your resume and match what this role '
                'asks for — keep them front and center in your skills section and summary.</div>'
            )
            md(
                '<div style="margin-top:.65rem">'
                + ''.join(f'<span class="chip good">{esc(skill)}</span>' for skill in matched)
                + '</div>'
            )
        else:
            md(
                '<div class="body-copy">None of your current resume skills matched this role\u2019s '
                'explicit requirements yet — see the missing skills below.</div>'
            )
        _card_edge_bottom()


def _missing_skills(r: dict) -> None:
    """Technical gaps, grouped by priority — these genuinely require learning.

    Each priority level gets its own labeled, color-tinted block (label row,
    then its skill chips on the line below) instead of one flat inline row,
    so High/Medium/Low read as clearly separate groups rather than one
    run-on line of badges and chips.
    """
    with st.container(border=True, key="cv_card_missing_skills"):
        md('<div class="card-heading">Missing Technical Skills</div>')
        groups: list[str] = []
        for priority, kind in (("High", "high"), ("Medium", "medium"), ("Low", "neutral")):
            skills = [s for s in (r.get("missing_skills", []) or []) if s.get("priority") == priority]
            if not skills:
                continue
            chips_html = ''.join(
                f'<span class="chip {"warn" if priority == "High" else "neutral"}">{esc(item.get("skill", ""))}</span>'
                for item in skills
            )
            groups.append(
                f'<div class="priority-group {kind}">'
                f'<div class="priority-group-row">{badge(priority + " Priority", kind)}'
                f'<span class="priority-arrow">&#8594;</span>{chips_html}</div>'
                f'</div>'
            )
        if groups:
            md(
                '<div class="body-copy">Closing these — starting with High priority — is what raises your '
                'score beyond what rewriting alone can do. See Recommended Next Steps below for where to '
                'start.</div>'
            )
            md(''.join(groups))
        else:
            md('<div class="body-copy">No missing technical skills were identified for this role — nice work.</div>')
        _card_edge_bottom()


def _soft_skills(r: dict) -> None:
    """Soft skills the JD asks for. Unlike technical gaps, most candidates
    already have these — the fix is naming them on the resume, not learning
    them, so it's presented as a same-day, no-training-required lever."""
    items = r.get("soft_skills_from_jd", []) or []
    with st.container(border=True, key="cv_card_soft_skills"):
        md('<div class="card-heading">Soft Skills To Add From This Job</div>')
        md(
            '<div class="body-copy">Unlike the technical gaps above, these don\u2019t need new training — '
            'most candidates already have them. The fix is naming them explicitly so both the ATS scan '
            'and the recruiter see them.</div>'
        )
        if not items:
            md('<div class="body-copy skills-followup">No explicit soft-skill signals were found in this job description.</div>')
        else:
            for item in items:
                md(
                    '<div class="issue-row">'
                    f'<div>{chip(item.get("skill", ""))}</div>'
                    f'<div class="issue-copy"><b>{esc(item.get("how_to_add", ""))}</b>'
                    f'<div>{esc(item.get("why_relevant", ""))}</div></div>'
                    '</div>'
                )
        _card_edge_bottom()


def _summary(r: dict, profile: dict) -> None:
    with st.container(border=True, key="cv_card_summary"):
        has_summary = bool(r.get("has_summary", True))
        before_text = str((profile or {}).get("summary") or "").strip()
        after_text = r.get("summary", "No improved summary was generated.")

        heading_label = "Resume Summary — Before & After" if (has_summary and before_text) else "Resume Summary — Suggested (none found on resume)"
        md(f'<div class="card-heading">{esc(heading_label)}</div>')

        if not has_summary or not before_text:
            md(
                '<div class="body-copy">Your resume does not currently include a professional summary or '
                'objective. Adding a short one at the top gives ATS systems and recruiters an immediate, '
                'keyword-rich pitch. The version below is built only from facts already present elsewhere '
                'on your resume:</div>'
            )
            before_text = "No summary currently on your resume."

        md(
            '<div class="rewrite-grid">'
            f'<div class="ba-card"><div class="lbl">BEFORE</div><div class="txt">{esc(before_text)}</div></div>'
            f'<div class="ba-card after"><div class="lbl">AFTER (SUGGESTED)</div><div class="txt">{esc(after_text)}</div></div>'
            '</div>'
        )
        md('<div style="height:.85rem"></div>')
        spacer, action = st.columns([4.6, 1.0], gap="small")
        with action:
            if st.button("Copy", type="primary", use_container_width=True, key="cv_copy_summary"):
                st.session_state["copied"] = True
        if st.session_state.get("copied"):
            md('<div class="copy-note">Summary copied below for easy use.</div>')
            st.code(after_text, language=None)
        _card_edge_bottom()


def _skills_section(r: dict, profile: dict) -> None:
    """The skills block itself, before and after: current skills as they sit
    on the resume today, versus an ATS-optimised version that folds in the
    soft skills above and clearly separates learn-first gaps."""
    skills = r.get("skills_section", {}) or {}
    with st.container(border=True, key="cv_card_skills_section"):
        md('<div class="card-heading">Skills Section — Before & After</div>')

        before_list = list((profile or {}).get("skills", []) or [])
        before_html = (
            ''.join(f'<span class="chip neutral">{esc(s)}</span>' for s in before_list)
            if before_list
            else '<div class="txt">No skills section was detected on your resume.</div>'
        )

        recommended = skills.get("recommended", []) or []
        add_later = skills.get("missing_to_add_after_learning", []) or []
        soft = [item.get("skill", "") for item in (r.get("soft_skills_from_jd", []) or []) if item.get("skill")]

        after_parts: list[str] = []
        if recommended:
            after_parts.append(''.join(f'<span class="chip good">{esc(s)}</span>' for s in recommended))
        if soft:
            after_parts.append('<div class="body-copy skills-followup"><b>Soft skills</b></div>')
            after_parts.append(''.join(f'<span class="chip">{esc(s)}</span>' for s in soft))
        if add_later:
            after_parts.append('<div class="body-copy skills-followup"><b>Add only after learning</b></div>')
            after_parts.append(''.join(f'<span class="chip warn">{esc(s)}</span>' for s in add_later))
        after_html = ''.join(after_parts) if after_parts else '<div class="txt">No ATS-optimised skills section was generated.</div>'

        md(
            '<div class="rewrite-grid">'
            f'<div class="ba-card"><div class="lbl">BEFORE</div>{before_html}</div>'
            f'<div class="ba-card after"><div class="lbl">AFTER (SUGGESTED)</div>{after_html}</div>'
            '</div>'
        )
        why = skills.get("why", "")
        if why:
            md(f'<div class="why-box"><b>Why this is better:</b> {esc(why)}</div>')
        _card_edge_bottom()


def _rewrite_group(title: str, items: list[dict], *, kind: str) -> None:
    if not items:
        return
    with st.container(border=True, key=f"cv_card_rewrite_{kind}"):
        _card_edge_bottom()
        md(f'<div class="card-heading">{esc(title)} <span class="badge good">ATS-FOCUSED</span></div>')
        for index, item in enumerate(items, start=1):
            if kind == "experience":
                label = f'{esc(item.get("role", "Experience"))} · {esc(item.get("company", ""))}'
            elif kind == "project":
                label = esc(item.get("project", "Project"))
            elif kind == "certification":
                label = esc(item.get("certification", "Certification"))
            elif kind == "achievement":
                label = esc(item.get("achievement", "Achievement"))
            else:
                label = "Resume Bullet"

            md(
                '<div class="rewrite-row">'
                f'<div class="rewrite-index">{index}</div>'
                '<div>'
                f'<div class="rewrite-title">{label}</div>'
                '<div class="rewrite-grid">'
                f'<div class="ba-card"><div class="lbl">BEFORE</div><div class="txt">{esc(item.get("before", ""))}</div></div>'
                f'<div class="ba-card after"><div class="lbl">AFTER (SUGGESTED)</div><div class="txt">{esc(item.get("after", ""))}</div></div>'
                '</div>'
                f'<div class="why-box"><b>Why this is better:</b> {esc(item.get("why", ""))}</div>'
                '</div></div>'
            )
        _card_edge_bottom()


def _recommendations(r: dict) -> None:
    with st.container(border=True, key="cv_card_recommendations"):
        tag = sample_badge() if r.get("source") == "sample" else ""
        md(f'<div class="card-heading">Recommended Next Steps {tag}</div>')
        md(
            '<div class="body-copy skills-followup" style="margin-bottom:.85rem">Prioritised actions to raise your ATS score, plus '
            'quick fixes that need no new skills at all.</div>'
        )
        recommendations = r.get("recommendations", []) or []
        if not recommendations:
            md('<div class="body-copy">No additional recommendations were generated.</div>')
        else:
            for index, recommendation in enumerate(recommendations, start=1):
                md(
                    f'<div class="rec"><div class="n">{index}</div>'
                    f'<div class="t">{esc(recommendation)}</div></div>'
                )

        issues = r.get("resume_issues", []) or []
        if issues:
            md('<div class="body-copy skills-followup" style="margin-top:.9rem"><b>Other quick fixes</b></div>')
            for issue in issues:
                severity = str(issue.get("severity", "Review"))
                badge_kind = {"High": "high", "Medium": "medium", "Low": "neutral"}.get(severity, "neutral")
                md(
                    '<div class="issue-row">'
                    f'<div>{badge(severity, badge_kind)}</div>'
                    f'<div class="issue-copy"><b>{esc(issue.get("issue", ""))}</b>'
                    f'<div>{esc(issue.get("fix", ""))}</div></div>'
                    '</div>'
                )
        _card_edge_bottom()


def render() -> None:
    st.markdown(CV_PAGE_CSS, unsafe_allow_html=True)
    page_header(
        "CV Improvement",
        "CV Improvement",
        "Make your resume stronger for a specific target role.",
    )

    job = st.session_state[C.SS_TARGET_JOB]
    if job is None and (state.profile_is_sample() or st.session_state[C.SS_DEMO_MODE]):
        job = sd.SAMPLE_TARGET_JOB

    if job is None:
        empty_state(
            "No target job selected.",
            "Pick a job from Job Match (or turn on Sample-data preview) to get tailored CV suggestions.",
            icon="briefcase",
        )
        if st.button("Go to Job Match", type="primary", key="cv_go_jobs"):
            state.go_to(C.PAGE_JOBS)
            st.rerun()
        return

    _target_job_card(job)
    _gap()
    result = st.session_state[C.SS_CV_RESULT]
    if result is None:
        with st.spinner("Generating ATS-focused improvements..."):
            try:
                result = backend.improve_cv(state.profile(), job)
            except backend.BackendError as exc:
                st.error(str(exc))
                return
        st.session_state[C.SS_CV_RESULT] = result

    profile = state.profile() or {}

    _ats_score(result)
    _gap()
    _matched_skills(result)
    _gap()
    _missing_skills(result)
    _gap()
    _soft_skills(result)
    _gap()
    _summary(result, profile)
    _gap()
    _skills_section(result, profile)
    _gap()
    _rewrite_group("Experience, Internship & Part-Time Rewrites", result.get("experience_rewrites", []) or [], kind="experience")
    if result.get("experience_rewrites"):
        _gap()
    _rewrite_group("Project Description Rewrites", result.get("project_rewrites", []) or [], kind="project")
    if result.get("project_rewrites"):
        _gap()
    _rewrite_group("Certification Rewrites", result.get("certification_rewrites", []) or [], kind="certification")
    if result.get("certification_rewrites"):
        _gap()
    _rewrite_group("Achievements & Leadership Rewrites", result.get("achievement_rewrites", []) or [], kind="achievement")
    if result.get("achievement_rewrites"):
        _gap()
    _rewrite_group("Additional Bullet Improvements", result.get("bullets", []) or [], kind="bullet")
    if result.get("bullets"):
        _gap()
    _recommendations(result)

    st.markdown('<div class="next-action-gap"></div>', unsafe_allow_html=True)
    left_spacer, action = st.columns([4.2, 1.3], gap="small")
    with action:
        if st.button("Next: AI Career Mentor →", type="primary", use_container_width=True, key="cv_next_mentor"):
            state.go_to(C.PAGE_MENTOR)
            st.rerun()