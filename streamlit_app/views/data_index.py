"""Page 5 - Dataset & Index Management."""
from __future__ import annotations

import streamlit as st

from .. import backend, sample_data as sd
from ..components import (badge, esc, md, metric_row, page_header, sample_badge,
                          vertical_pipeline)


def render() -> None:
    page_header("Data & Index", "Dataset & Index Management", "Manage the job dataset, derived vector index and career knowledge base.")

    m = backend.get_dataset_metrics()
    md(f'<div class="sh-card-title"><span class="left">Dataset</span>{sample_badge("SAMPLE DATA") if m.get("source") == "sample" else badge("LIVE DATA", "good")}</div>')
    metric_row([
        ("Total Jobs", m["total_jobs"], "Naukri job postings", ""),
        ("Data Scientist Jobs", m["ds_jobs"], "category count", "accent"),
        ("Software Engineer Jobs", m["se_jobs"], "category count", "accent"),
        ("Valid Records", m["valid"], "after cleaning", "good"),
    ])

    left, right = st.columns([1.15, 1])
    with left:
        md('<div class="sh-card">')
        md('<div class="sh-card-title"><span class="left">Index Status</span></div>')
        for i in backend.get_index_status():
            md(
                f'<div class="idx"><div><div class="n">{esc(i["name"])}</div><div class="d">{esc(i["detail"])}</div></div>'
                f'{badge("Ready", "good") if i["ready"] else badge("Not built", "medium")}</div>'
            )
        md('<div style="height:.8rem"></div>')
        a, b = st.columns(2)
        with a:
            if st.button("Rebuild Index", type="primary", use_container_width=True, help="Optional: regenerate the derived index from the committed CSV."):
                with st.spinner("Rebuilding index..."):
                    res = backend.rebuild_index()
                st.info(res["message"])
        with b:
            if st.button("Refresh Data", use_container_width=True):
                with st.spinner("Refreshing dataset..."):
                    res = backend.refresh_data()
                st.info(res["message"])
        md('</div>')

    with right:
        md('<div class="sh-card">')
        md('<div class="sh-card-title"><span class="left">Data Pipeline</span><span class="badge accent">6 stages</span></div>')
        index_ready = any(i['name'] == 'FAISS Index' and i['ready'] for i in backend.get_index_status())
        md(vertical_pipeline(sd.DATA_PIPELINE, done_upto=6 if index_ready else 5))
        md('</div>')
