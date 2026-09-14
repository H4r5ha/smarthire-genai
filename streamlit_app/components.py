"""Reusable HTML/Streamlit UI building blocks for the SmartHire design system."""
from __future__ import annotations

import html
from typing import Iterable

import streamlit as st

# ---------------------------------------------------------------------------
# Icons (inline SVG so we do not depend on emoji)
# ---------------------------------------------------------------------------
ICONS = {
    "upload": '<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/></svg>',
    "doc": '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>',
    "search": '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    "chat": '<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "briefcase": '<svg viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    "pin": '<svg viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "mail": '<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/></svg>',
    "db": '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.7-4 3-9 3s-9-1.3-9-3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/></svg>',
    "shield": '<svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "user": '<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "check": '<svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"/></svg>',
    "chart": '<svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 15l4-4 4 4 5-6"/></svg>',
    "spark": '<svg viewBox="0 0 24 24"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/></svg>',
}


def esc(text: str) -> str:
    return html.escape(str(text))


def md(markup: str) -> None:
    """Render raw HTML markup."""
    st.markdown(markup, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page-level
# ---------------------------------------------------------------------------
def page_header(kicker: str, title: str, subtitle: str) -> None:
    md(
        f'<h1 class="sh-title">{esc(title)}</h1>'
        f'<p class="sh-subtitle">{esc(subtitle)}</p>'
    )


def sample_badge(label: str = "SAMPLE") -> str:
    return f'<span class="badge sample">{esc(label)}</span>'


def badge(label: str, kind: str = "neutral") -> str:
    return f'<span class="badge {kind}">{esc(label)}</span>'


def chip(label: str, kind: str = "") -> str:
    return f'<span class="chip {kind}">{esc(label)}</span>'


def chips(labels: Iterable[str], kind: str = "") -> str:
    return "".join(chip(l, kind) for l in labels)


def card_title(title: str, right_html: str = "", icon: str | None = None) -> str:
    ico = f'<span style="color:var(--accent);width:16px;height:16px;display:inline-flex">{_svg(icon)}</span>' if icon else ""
    return f'<div class="sh-card-title"><span class="left">{ico}{esc(title)}</span><span>{right_html}</span></div>'


def _svg(name: str | None) -> str:
    if not name:
        return ""
    return ICONS[name].replace("<svg ", '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" ')


def metric_card(label: str, value: str, hint: str = "", tone: str = "", icon: str | None = None) -> str:
    ico = f'<span style="display:inline-flex;color:var(--accent)">{_svg(icon)}</span>' if icon else ""
    hint_html = f'<div class="h">{esc(hint)}</div>' if hint else ""
    return (
        f'<div class="sh-metric"><div class="l">{ico}{esc(label)}</div>'
        f'<div class="v {tone}">{esc(value)}</div>{hint_html}</div>'
    )


def metric_row(items: list[tuple], cols: int | None = None) -> None:
    """items: list of (label, value, hint, tone) tuples."""
    columns = st.columns(cols or len(items))
    for col, item in zip(columns, items):
        label, value, hint, tone = (list(item) + ["", "", ""])[:4]
        with col:
            md(metric_card(label, value, hint, tone))


def empty_state(title: str, body: str, icon: str = "doc") -> None:
    md(
        f'<div class="sh-empty"><div class="ico">{ICONS[icon]}</div>'
        f'<h4>{esc(title)}</h4><p>{esc(body)}</p></div>'
    )


def error_state(title: str, body: str = "") -> None:
    md(
        f'<div class="sh-card" style="border-color:#F3C4BC;background:var(--danger-soft)">'
        f'<div style="font-weight:600;color:var(--danger);font-size:14px">{esc(title)}</div>'
        f'<div style="font-size:12.5px;color:var(--muted);margin-top:.2rem">{esc(body)}</div></div>'
    )


def ring(percent: int, tone: str = "", size: str = "") -> str:
    return f'<div class="ring {tone} {size}" style="--p:{int(percent)}"><span>{int(percent)}%</span></div>'


def score_pill(score: int) -> str:
    kind = "strong" if score >= 85 else "mid" if score >= 70 else "low"
    return f'<span class="score-pill {kind}">{score}% Match</span>'


def horizontal_pipeline(stages: list[str], highlight_last: bool = True) -> str:
    parts = []
    for i, s in enumerate(stages):
        cls = "st llm" if highlight_last and i == len(stages) - 1 else "st"
        dot = "" if cls == "st llm" else "<i></i>"
        parts.append(f'<span class="{cls}">{dot}{esc(s)}</span>')
        if i < len(stages) - 1:
            parts.append('<span class="ar">→</span>')
    return f'<div class="pipe">{"".join(parts)}</div>'


def vertical_pipeline(steps: list[tuple[str, str]], done_upto: int | None = None) -> str:
    out = []
    for i, (t, s) in enumerate(steps, start=1):
        cls = "step done" if done_upto is not None and i <= done_upto else "step"
        out.append(f'<div class="{cls}"><div class="n">{i}</div><div class="t">{esc(t)}</div><div class="s">{esc(s)}</div></div>')
    return f'<div class="vpipe">{"".join(out)}</div>'


def status_dot(ok: bool, on: str = "Ready", off: str = "Not built") -> str:
    return f'<span><span class="dot {"g" if ok else "a"}"></span>{on if ok else off}</span>'
