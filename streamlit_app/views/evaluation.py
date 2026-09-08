"""Page 6 - lightweight evaluation dashboard."""
from __future__ import annotations

import streamlit as st

from .. import backend, config as C
from ..components import badge, esc, md, metric_row, page_header


def render() -> None:
    page_header('Evaluation', 'Answer Quality Evaluation', 'Run a small retrieval benchmark and inspect the evidence-grounding design.')
    current = st.session_state.get(C.SS_EVAL)
    if st.button('Run Evaluation', type='primary'):
        with st.spinner('Running retrieval benchmark...'):
            try:
                current = backend.run_evaluation()
                st.session_state[C.SS_EVAL] = current
            except backend.BackendError as exc:
                st.error(str(exc))
                return
    if not current:
        md('<div class="sh-card"><div class="sh-card-title"><span class="left">Evaluation not run</span></div><div style="font-size:13px;color:var(--muted)">Run the benchmark to populate retrieval metrics. This starter benchmark uses 6 manually defined role queries; it is a development check, not a final academic evaluation.</div></div>')
        return
    o = current['overview']
    metric_row([
        ('Retrieval Top-1', f'{o["top1"]}%', 'expected category at rank 1', 'accent'),
        ('Retrieval Top-5', f'{o["top5"]}%', 'expected category within top 5', 'good'),
        ('Mentor Grounding', 'Manual', 'rate after testing mentor answers', ''),
        ('Helpfulness', 'Manual', 'rate with your evaluation rubric', ''),
    ])
    md('<div class="sh-card"><div class="sh-card-title"><span class="left">Retrieval Cases</span>'+badge('PROXY BENCHMARK','neutral')+'</div>')
    for row in current['rows']:
        md(
            '<div class="eval-row">'
            f'<div class="k">{esc(row["expected"])}</div>'
            f'<div><b>{esc(row["query"])}</b><br><span style="color:var(--muted)">Top-1: {row["top1"]} · Top-5: {row["top5"]} · first category: {esc(row["best_category"])}</span></div>'
            '</div>'
        )
    md('</div>')
    st.caption('For the final report, add a larger manually-labelled test set and human ratings for correctness, grounding and helpfulness as required by the project brief.')
