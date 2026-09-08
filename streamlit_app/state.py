"""Session-state initialisation and small helpers."""
from __future__ import annotations

import streamlit as st

from . import config as C


DEFAULTS = {
    C.SS_PAGE: C.PAGE_RESUME,
    C.SS_PROFILE: None,
    C.SS_PROFILE_STATE: "idle",
    C.SS_DEMO_MODE: False,
    C.SS_JOB_QUERY: "",
    C.SS_JOB_DESCRIPTION: "",
    C.SS_JOB_RESULTS: None,
    C.SS_JOB_STATE: "idle",
    C.SS_TARGET_JOB: None,
    C.SS_CV_RESULT: None,
    C.SS_CHAT: [],
    C.SS_MENTOR_STATE: "idle",
    C.SS_INDEX_STATUS: None,
    C.SS_EVAL: None,
}


def init_state() -> None:
    import copy
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(value)


def go_to(page: str) -> None:
    st.session_state[C.SS_PAGE] = page


def current_page() -> str:
    return st.session_state[C.SS_PAGE]


def profile() -> dict | None:
    return st.session_state.get(C.SS_PROFILE)


def profile_is_sample() -> bool:
    p = profile()
    return bool(p and p.get("source") == "sample")


def clear_profile() -> None:
    st.session_state[C.SS_PROFILE] = None
    st.session_state[C.SS_PROFILE_STATE] = "idle"
    st.session_state[C.SS_JOB_RESULTS] = None
    st.session_state[C.SS_JOB_DESCRIPTION] = ""
    st.session_state[C.SS_JOB_STATE] = "idle"
    st.session_state[C.SS_CV_RESULT] = None
    st.session_state[C.SS_CHAT] = []
