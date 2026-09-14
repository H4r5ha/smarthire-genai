"""Central configuration for the SmartHire GenAI Streamlit UI."""

APP_NAME = "SmartHire"
APP_SUFFIX = "GenAI"
APP_TAGLINE = "Resume Matching & AI Career Mentor"
APP_PROMISE = "From your resume to a better career."

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
PAGE_RESUME = "Resume Analysis"
PAGE_JOBS = "Job Match"
PAGE_CV = "CV Improvement"
PAGE_MENTOR = "AI Career Mentor"
PAGE_DATA = "Data & Index"
PAGE_EVAL = "Evaluation"

WORKFLOW_PAGES = [PAGE_RESUME, PAGE_JOBS, PAGE_CV, PAGE_MENTOR]
PROJECT_PAGES = [PAGE_DATA, PAGE_EVAL]
ALL_PAGES = WORKFLOW_PAGES + PROJECT_PAGES

# Small inline SVG icons (Lucide-style, stroke based) keyed by page name.
NAV_ICONS = {
    PAGE_RESUME: '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h8"/></svg>',
    PAGE_JOBS: '<svg viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    PAGE_CV: '<svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>',
    PAGE_MENTOR: '<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    PAGE_DATA: '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.7-4 3-9 3s-9-1.3-9-3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/></svg>',
    PAGE_EVAL: '<svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 15l4-4 4 4 5-6"/></svg>',
}

# ---------------------------------------------------------------------------
# Session-state keys
# ---------------------------------------------------------------------------
SS_PAGE = "page"
SS_PROFILE = "candidate_profile"
SS_PROFILE_STATE = "profile_state"          # idle | parsing | ready | error
SS_DEMO_MODE = "demo_mode"
SS_JOB_QUERY = "job_query"
SS_JOB_DESCRIPTION = "job_description"
SS_JOB_RESULTS = "job_results"
SS_JOB_STATE = "job_state"                  # idle | searching | ready | empty
SS_TARGET_JOB = "target_job"
SS_CV_RESULT = "cv_result"
SS_CHAT = "chat_history"
SS_MENTOR_STATE = "mentor_state"            # idle | thinking
SS_INDEX_STATUS = "index_status"
SS_EVAL = "evaluation_results"

# ---------------------------------------------------------------------------
# Accepted upload types
# ---------------------------------------------------------------------------
RESUME_FILE_TYPES = ["pdf", "docx", "txt"]
MAX_UPLOAD_MB = 10

# Privacy-mode upload: candidate crops out the personal-info section of their
# resume and uploads only screenshot(s) of the rest (skills/experience/education).
RESUME_IMAGE_FILE_TYPES = ["png", "jpg", "jpeg", "webp"]
MAX_RESUME_IMAGES = 4