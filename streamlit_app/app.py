"""
SmartHire GenAI — Streamlit UI entry point.

Run from the repository root:
    streamlit run streamlit_app/app.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

import streamlit as st

# Allow `python -m streamlit run streamlit_app/app.py` to resolve package imports.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from streamlit_app import config as C, state  # noqa: E402
from streamlit_app import backend as app_backend  # noqa: E402
from streamlit_app.sidebar import render_sidebar  # noqa: E402
from streamlit_app.styles import inject_css  # noqa: E402
from streamlit_app.views import (cv_improvement, data_index, evaluation, job_match,  # noqa: E402
                                 mentor, resume_analysis)

PAGES = {
    C.PAGE_RESUME: resume_analysis.render,
    C.PAGE_JOBS: job_match.render,
    C.PAGE_CV: cv_improvement.render,
    C.PAGE_MENTOR: mentor.render,
    C.PAGE_DATA: data_index.render,
    C.PAGE_EVAL: evaluation.render,
}


def main() -> None:
    st.set_page_config(
        page_title=f"{C.APP_NAME} {C.APP_SUFFIX} · {C.APP_TAGLINE}",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    state.init_state()
    render_sidebar()

    # Deployment-safe initialization: the vector index is generated automatically
    # from the committed CSV when no cached artifact exists. A local vectorstore
    # is therefore an optimization, never a prerequisite for deployment.
    if 'index_bootstrap_status' not in st.session_state:
        with st.spinner('Preparing the job search index...'):
            st.session_state.index_bootstrap_status = state_backend = app_backend.prepare_index()
        if not state_backend.get('ok'):
            st.warning('The job index could not be prepared yet. Job matching and the RAG mentor may be unavailable until the dataset/index is fixed.')

    render = PAGES.get(state.current_page(), resume_analysis.render)
    try:
        render()
    except Exception:  # never show raw tracebacks to end users
        # The real traceback goes to server logs only (never the UI) so a bug
        # like this is diagnosable from `streamlit run` output / Cloud logs
        # instead of only ever showing as a generic banner.
        print("[SmartHire] Unhandled error while rendering a page:", file=sys.stderr)
        traceback.print_exc()
        st.error("Something went wrong while rendering this page. Please try again or switch pages.")


if __name__ == "__main__":
    main()
