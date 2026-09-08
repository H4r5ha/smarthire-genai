import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root{
  --bg:#F7F4EE; --card:#FFFFFF; --card-soft:#FBFAF7; --border:#E7E2D9; --border-strong:#D9D3C8;
  --text:#1B1F2E; --muted:#6B7080; --faint:#9AA0AE;
  --accent:#4F46E5; --accent-soft:#EEF0FF; --accent-border:#D6D9FF;
  --success:#1F8A5B; --success-soft:#E7F5EE; --warn:#B7791F; --warn-soft:#FDF3E1; --danger:#C0392B; --danger-soft:#FBEAE7;
  --navy:#171B2B; --navy-2:#1F2437; --navy-border:#2B3147;
  --r-card:16px; --r-sm:10px; --shadow:0 1px 2px rgba(20,20,40,.04), 0 6px 20px -12px rgba(20,20,40,.10);
}

/* ---------- App shell ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp{ background:var(--bg) !important; color:var(--text); font-family:'Inter',system-ui,sans-serif; }
[data-testid="stHeader"]{ background:transparent; }
#MainMenu, footer, [data-testid="stDecoration"]{ visibility:hidden; height:0; }
.block-container{ padding:2.2rem 2.6rem 4rem 2.6rem !important; max-width:1280px; }
h1,h2,h3,h4{ font-family:'Space Grotesk',sans-serif !important; color:var(--text); letter-spacing:-0.01em; }
p, li, label, .stMarkdown{ color:var(--text); }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"]{ background:var(--navy) !important; border-right:1px solid var(--navy-border); min-width:264px !important; max-width:264px !important; }
[data-testid="stSidebar"] > div:first-child{ padding:1.2rem 1rem 2rem 1rem; }
[data-testid="stSidebar"] *{ color:#E6E8F0; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{ gap:.3rem; }
.sh-brand{ display:flex; align-items:center; gap:.7rem; padding:.3rem .4rem 1.1rem .4rem; }
.sh-brand .logo{ width:34px; height:34px; border-radius:10px; background:linear-gradient(135deg,#6366F1,#4338CA); display:grid; place-items:center; font-size:18px; color:#fff; box-shadow:0 6px 16px -6px rgba(99,102,241,.7); }
.sh-brand .name{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:17px; line-height:1.1; }
.sh-brand .sub{ font-size:9.5px; letter-spacing:.18em; color:#8C93A8; font-weight:600; }
.sh-section{ font-size:10px; letter-spacing:.16em; color:#7D8499; font-weight:600; margin:.9rem .5rem .35rem .5rem; }

/* Nav buttons: secondary = idle, primary = active */
[data-testid="stSidebar"] .stButton > button{
  width:100%; justify-content:flex-start; border-radius:10px; border:1px solid transparent; background:transparent;
  color:#C9CDDA; font-weight:500; font-size:13.5px; padding:.5rem .8rem; min-height:38px; transition:all .15s;
}
[data-testid="stSidebar"] .stButton > button:hover{ background:var(--navy-2); color:#fff; border-color:var(--navy-border); }
[data-testid="stSidebar"] .stButton > button[kind="primary"]{ background:var(--accent) !important; color:#fff !important; border-color:var(--accent) !important; box-shadow:0 6px 16px -8px rgba(79,70,229,.8); }
[data-testid="stSidebar"] .stButton > button p{ font-size:13.5px; }

.sh-side-card{ background:var(--navy-2); border:1px solid var(--navy-border); border-radius:14px; padding:.85rem .9rem; margin-top:.9rem; }
.sh-side-card .lbl{ font-size:10px; letter-spacing:.14em; color:#7D8499; font-weight:600; margin-bottom:.5rem; }
.sh-side-card .row{ display:flex; justify-content:space-between; align-items:center; font-size:12.5px; color:#C9CDDA; padding:.22rem 0; }
.sh-side-card .who{ display:flex; gap:.6rem; align-items:center; }
.sh-side-card .avatar{ width:32px; height:32px; border-radius:50%; background:var(--accent-soft); color:var(--accent); font-weight:700; display:grid; place-items:center; font-family:'Space Grotesk'; }
.sh-side-card .who .n{ font-weight:600; font-size:13.5px; color:#fff; }
.sh-side-card .who .r{ font-size:11.5px; color:#9AA0B5; }
.sh-side-card .ok{ color:#7ED9A8; font-size:11.5px; margin-top:.4rem; }
.sh-side-card .empty{ color:#9AA0B5; font-size:12px; line-height:1.4; }
.dot{ display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:6px; }
.dot.g{ background:#34D399; box-shadow:0 0 0 3px rgba(52,211,153,.18); }
.dot.a{ background:#FBBF24; box-shadow:0 0 0 3px rgba(251,191,36,.18); }
.dot.r{ background:#F87171; }
[data-testid="stSidebar"] [data-testid="stToggle"] label p, [data-testid="stSidebar"] [data-testid="stCheckbox"] label p{ font-size:12.5px; color:#C9CDDA; }

/* ---------- Page header ---------- */
.sh-kicker{ font-size:10.5px; letter-spacing:.18em; color:var(--accent); font-weight:600; margin-bottom:.35rem; }
.sh-title{ font-family:'Space Grotesk',sans-serif; font-size:26px; font-weight:700; color:var(--text); margin:0; line-height:1.15; }
.sh-subtitle{ color:var(--muted); font-size:14px; margin:.35rem 0 1.4rem 0; max-width:720px; }

/* ---------- Cards ---------- */
.sh-card{ background:var(--card); border:1px solid var(--border); border-radius:var(--r-card); padding:1.15rem 1.25rem; box-shadow:var(--shadow); margin-bottom:1rem; }
.sh-card.soft{ background:var(--card-soft); }
.sh-card.tight{ padding:.9rem 1rem; }
.sh-card-title{ font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:15px; margin-bottom:.6rem; display:flex; align-items:center; gap:.5rem; justify-content:space-between; }
.sh-card-title .left{ display:flex; align-items:center; gap:.5rem; }
.sh-metric{ background:var(--card); border:1px solid var(--border); border-radius:14px; padding:.95rem 1.1rem; box-shadow:var(--shadow); min-height:92px; }
.sh-metric .l{ font-size:11.5px; color:var(--muted); font-weight:500; display:flex; align-items:center; gap:.4rem; }
.sh-metric .v{ font-family:'Space Grotesk',sans-serif; font-size:26px; font-weight:700; margin-top:.25rem; color:var(--text); }
.sh-metric .v.good{ color:var(--success); } .sh-metric .v.accent{ color:var(--accent); } .sh-metric .v.warn{ color:var(--warn); }
.sh-metric .h{ font-size:11.5px; color:var(--faint); margin-top:.15rem; }

/* ---------- Chips / badges ---------- */
.chip{ display:inline-block; padding:.28rem .65rem; border-radius:999px; font-size:12px; font-weight:500; margin:0 .35rem .4rem 0; border:1px solid var(--accent-border); background:var(--accent-soft); color:#3730A3; }
.chip.neutral{ background:#F3F1EC; border-color:var(--border); color:#4B5060; }
.chip.warn{ background:var(--warn-soft); border-color:#F3DFB6; color:#92400E; }
.chip.good{ background:var(--success-soft); border-color:#BFE6D1; color:#166534; }
.badge{ display:inline-flex; align-items:center; gap:.3rem; padding:.18rem .55rem; border-radius:999px; font-size:10.5px; font-weight:600; letter-spacing:.04em; }
.badge.sample{ background:var(--warn-soft); color:#92400E; border:1px solid #F3DFB6; }
.badge.good{ background:var(--success-soft); color:var(--success); border:1px solid #BFE6D1; }
.badge.accent{ background:var(--accent-soft); color:var(--accent); border:1px solid var(--accent-border); }
.badge.neutral{ background:#F3F1EC; color:var(--muted); border:1px solid var(--border); }
.badge.danger{ background:var(--danger-soft); color:var(--danger); border:1px solid #F3C4BC; }
.badge.high{ background:var(--danger-soft); color:#9F2A1E; border:1px solid #F3C4BC; }
.badge.medium{ background:var(--warn-soft); color:#92400E; border:1px solid #F3DFB6; }

/* ---------- Buttons (main area) ---------- */
.stButton > button{ border-radius:10px; font-weight:600; font-size:13px; padding:.45rem 1rem; min-height:38px; border:1px solid var(--border-strong); background:#fff; color:var(--text); box-shadow:0 1px 1px rgba(0,0,0,.02); transition:all .15s; }
.stButton > button:hover{ border-color:var(--accent); color:var(--accent); background:#fff; }
.stButton > button[kind="primary"]{ background:var(--accent); border-color:var(--accent); color:#fff; box-shadow:0 8px 18px -10px rgba(79,70,229,.7); }
.stButton > button[kind="primary"]:hover{ background:#4338CA; color:#fff; }
.stButton > button:focus{ box-shadow:0 0 0 3px rgba(79,70,229,.18) !important; }

/* ---------- Inputs ---------- */
[data-testid="stTextInput"] input, [data-testid="stChatInput"] textarea{ border-radius:12px !important; border:1px solid var(--border-strong) !important; background:#fff !important; font-size:14px; color:var(--text); }
[data-testid="stTextInput"] > div > div{ border-radius:12px; border:none !important; background:transparent; }
[data-testid="stTextInput"] input:focus{ border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(79,70,229,.15); }
[data-testid="stChatInput"]{ border-radius:14px; border:1px solid var(--border-strong); background:#fff; }
[data-testid="stChatInput"] > div{ border:none !important; }
[data-testid="stFileUploader"] section{ background:transparent; border:none; padding:0; }
[data-testid="stFileUploader"] section > div{ color:var(--muted); }
[data-testid="stFileUploader"] button{ border-radius:10px; border:1px solid var(--border-strong); background:#fff; color:var(--text); font-weight:600; }
[data-testid="stFileUploaderDropzone"]{ background:var(--card-soft) !important; border:1.5px dashed var(--accent-border) !important; border-radius:14px !important; }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"]{ gap:.25rem; border-bottom:1px solid var(--border); background:transparent; }
.stTabs [data-baseweb="tab"]{ height:38px; padding:0 .9rem; border-radius:8px 8px 0 0; color:var(--muted); font-size:13px; font-weight:500; background:transparent; }
.stTabs [aria-selected="true"]{ color:var(--accent) !important; font-weight:600; }
.stTabs [data-baseweb="tab-highlight"]{ background:var(--accent); height:2px; }
.stTabs [data-baseweb="tab-border"]{ background:transparent; }

/* ---------- Progress / misc ---------- */
[data-testid="stProgress"] > div > div{ background:var(--accent-soft); border-radius:999px; }
[data-testid="stProgress"] > div > div > div{ background:var(--accent); border-radius:999px; }
[data-testid="stExpander"]{ border:1px solid var(--border); border-radius:12px; background:#fff; }
.stAlert{ border-radius:12px; }
hr{ border-color:var(--border) !important; }

/* ---------- Upload card ---------- */
.sh-upload{ border:1.5px dashed var(--accent-border); border-radius:16px; background:var(--card-soft); padding:1.6rem 1rem .6rem 1rem; text-align:center; }
.sh-upload .ico{ width:52px; height:52px; border-radius:14px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; margin:0 auto .7rem auto; }
.sh-upload .ico svg{ width:26px; height:26px; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
.sh-upload h3{ font-size:16px; margin:.1rem 0; }
.sh-upload p{ color:var(--muted); font-size:12.5px; margin:0 0 .6rem 0; }

/* ---------- Empty state ---------- */
.sh-empty{ text-align:center; padding:2.6rem 1rem; border:1px dashed var(--border-strong); border-radius:16px; background:var(--card-soft); }
.sh-empty .ico{ width:46px; height:46px; margin:0 auto .7rem auto; border-radius:12px; background:#fff; border:1px solid var(--border); display:grid; place-items:center; color:var(--accent); }
.sh-empty .ico svg{ width:22px; height:22px; fill:none; stroke:currentColor; stroke-width:1.7; stroke-linecap:round; stroke-linejoin:round; }
.sh-empty h4{ margin:0 0 .25rem 0; font-size:15px; }
.sh-empty p{ color:var(--muted); font-size:13px; margin:0; }

/* ---------- Profile ---------- */
.sh-avatar-lg{ width:56px; height:56px; border-radius:16px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; font-family:'Space Grotesk'; font-weight:700; font-size:24px; border:1px solid var(--accent-border); }
.sh-kv{ font-size:12.5px; color:var(--muted); display:flex; gap:.4rem; align-items:center; margin:.15rem 0; }
.sh-kv svg{ width:14px; height:14px; fill:none; stroke:currentColor; stroke-width:1.8; }
.ring{ --p:0; width:96px; height:96px; border-radius:50%; background:conic-gradient(var(--success) calc(var(--p)*1%), #E8F0EA 0); display:grid; place-items:center; margin:0 auto; }
.ring.accent{ background:conic-gradient(var(--accent) calc(var(--p)*1%), var(--accent-soft) 0); }
.ring.warn{ background:conic-gradient(var(--warn) calc(var(--p)*1%), var(--warn-soft) 0); }
.ring > span{ width:74px; height:74px; border-radius:50%; background:#fff; display:grid; place-items:center; font-family:'Space Grotesk'; font-weight:700; font-size:20px; }
.ring.sm{ width:64px; height:64px; } .ring.sm > span{ width:48px; height:48px; font-size:14px; }
.check-list{ list-style:none; padding:0; margin:0; font-size:12.5px; color:var(--muted); }
.check-list li{ display:flex; gap:.45rem; align-items:center; padding:.16rem 0; }
.check-list .c{ width:14px; height:14px; border-radius:50%; display:grid; place-items:center; font-size:9px; color:#fff; background:var(--accent); }
.check-list .c.off{ background:#D5D2CB; }

/* ---------- Job cards ---------- */
.job-card{ background:#fff; border:1px solid var(--border); border-radius:16px; padding:1.05rem 1.2rem; box-shadow:var(--shadow); margin-bottom:.85rem; }
.job-card.top{ border-color:var(--accent-border); box-shadow:0 0 0 3px rgba(79,70,229,.06), var(--shadow); }
.job-rank{ font-family:'Space Grotesk'; font-weight:700; font-size:13px; color:var(--faint); letter-spacing:.06em; }
.job-title{ font-family:'Space Grotesk'; font-weight:600; font-size:16px; margin:.1rem 0 .05rem 0; }
.job-meta{ font-size:12.5px; color:var(--muted); }
.job-meta b{ color:var(--text); font-weight:600; }
.job-why{ font-size:12.5px; color:var(--muted); margin-top:.5rem; border-left:2px solid var(--accent-border); padding-left:.6rem; }
.score-pill{ display:inline-flex; align-items:center; gap:.35rem; padding:.3rem .7rem; border-radius:999px; font-family:'Space Grotesk'; font-weight:700; font-size:14px; }
.score-pill.strong{ background:var(--success-soft); color:var(--success); border:1px solid #BFE6D1; }
.score-pill.mid{ background:var(--accent-soft); color:var(--accent); border:1px solid var(--accent-border); }
.score-pill.low{ background:var(--warn-soft); color:var(--warn); border:1px solid #F3DFB6; }
.role-card{ background:#fff; border:1px solid var(--border); border-radius:14px; padding:.85rem 1rem; box-shadow:var(--shadow); display:flex; gap:.75rem; align-items:flex-start; }
.role-card .ico{ width:34px; height:34px; border-radius:10px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; flex:none; }
.role-card .ico svg{ width:17px; height:17px; fill:none; stroke:currentColor; stroke-width:1.8; }
.role-card .n{ font-weight:600; font-size:14px; }
.role-card .j{ font-size:12px; color:var(--muted); }
.role-card .r{ font-size:11.5px; color:var(--faint); margin-top:.2rem; }

/* ---------- CV improvement ---------- */
.ba-card{ border-radius:14px; padding:.9rem 1rem; border:1px solid var(--border); background:#F6F5F1; height:100%; }
.ba-card.after{ background:var(--success-soft); border-color:#BFE6D1; }
.ba-card .lbl{ font-size:10.5px; letter-spacing:.14em; font-weight:600; color:var(--muted); margin-bottom:.4rem; }
.ba-card.after .lbl{ color:var(--success); }
.ba-card .txt{ font-size:13.5px; line-height:1.55; }
.ba-arrow{ text-align:center; color:var(--accent); font-size:22px; padding-top:1.6rem; }
.why-box{ font-size:12.5px; color:var(--muted); background:#fff; border:1px solid var(--border); border-radius:10px; padding:.55rem .8rem; margin:.5rem 0 1rem 0; }
.why-box b{ color:var(--text); }
.rec{ display:flex; gap:.9rem; align-items:flex-start; background:#fff; border:1px solid var(--border); border-radius:14px; padding:.85rem 1rem; margin-bottom:.6rem; box-shadow:var(--shadow); }
.rec .n{ width:28px; height:28px; border-radius:9px; background:var(--accent); color:#fff; display:grid; place-items:center; font-family:'Space Grotesk'; font-weight:700; font-size:13px; flex:none; }
.rec .t{ font-size:14px; font-weight:500; padding-top:.25rem; }

/* ---------- Mentor ---------- */
.status-card{ background:#fff; border:1px solid var(--border); border-radius:14px; padding:.8rem 1rem; display:flex; gap:.75rem; align-items:center; box-shadow:var(--shadow); }
.status-card .ico{ width:34px; height:34px; border-radius:10px; display:grid; place-items:center; flex:none; }
.status-card .ico.g{ background:var(--success-soft); color:var(--success); } .status-card .ico.a{ background:var(--accent-soft); color:var(--accent); }
.status-card .ico svg{ width:17px; height:17px; fill:none; stroke:currentColor; stroke-width:1.9; stroke-linecap:round; stroke-linejoin:round; }
.status-card .t{ font-weight:600; font-size:13.5px; }
.status-card .s{ font-size:11.5px; color:var(--muted); }
.msg{ display:flex; gap:.7rem; margin-bottom:.9rem; }
.msg .av{ width:30px; height:30px; border-radius:9px; flex:none; display:grid; place-items:center; font-size:11px; font-weight:700; font-family:'Space Grotesk'; }
.msg.user{ flex-direction:row-reverse; }
.msg.user .av{ background:#E9E6DF; color:var(--text); }
.msg.bot .av{ background:var(--accent); color:#fff; }
.msg .bubble{ max-width:78%; border-radius:14px; padding:.7rem .95rem; font-size:13.5px; line-height:1.55; border:1px solid var(--border); }
.msg.user .bubble{ background:var(--accent-soft); border-color:var(--accent-border); border-top-right-radius:4px; }
.msg.bot .bubble{ background:#fff; border-top-left-radius:4px; box-shadow:var(--shadow); }
.msg .who{ font-size:10px; letter-spacing:.14em; font-weight:600; color:var(--faint); margin-bottom:.25rem; }
.msg .ts{ font-size:10.5px; color:var(--faint); margin-top:.35rem; }
.msg.bot .bubble.refused{ border-color:#F3DFB6; background:var(--warn-soft); }
.src{ background:#fff; border:1px solid var(--border); border-radius:12px; padding:.6rem .75rem; margin-bottom:.5rem; }
.src .t{ font-size:12.5px; font-weight:600; display:flex; gap:.4rem; }
.src .t .n{ color:var(--accent); }
.src .m{ font-size:11px; color:var(--muted); margin-top:.15rem; display:flex; justify-content:space-between; }
.src .bar{ height:4px; border-radius:999px; background:var(--accent-soft); margin-top:.4rem; overflow:hidden; }
.src .bar > i{ display:block; height:100%; background:var(--accent); }
.pipe{ display:flex; flex-wrap:wrap; align-items:center; gap:.35rem; }
.pipe .st{ background:#fff; border:1px solid var(--border); border-radius:999px; padding:.3rem .7rem; font-size:12px; font-weight:500; display:inline-flex; align-items:center; gap:.4rem; }
.pipe .st i{ width:7px; height:7px; border-radius:50%; background:var(--success); display:inline-block; }
.pipe .st.llm{ background:var(--accent-soft); border-color:var(--accent-border); color:var(--accent); font-weight:600; }
.pipe .ar{ color:var(--faint); font-size:12px; }
.vpipe{ position:relative; padding-left:2.1rem; }
.vpipe:before{ content:''; position:absolute; left:13px; top:10px; bottom:10px; width:2px; background:var(--accent-border); }
.vpipe .step{ position:relative; margin-bottom:.95rem; }
.vpipe .step .n{ position:absolute; left:-2.1rem; top:0; width:28px; height:28px; border-radius:50%; background:var(--accent); color:#fff; display:grid; place-items:center; font-size:12px; font-weight:700; font-family:'Space Grotesk'; border:3px solid var(--bg); }
.vpipe .step.done .n{ background:var(--success); }
.vpipe .step .t{ font-weight:600; font-size:13.5px; }
.vpipe .step .s{ font-size:12px; color:var(--muted); }

/* ---------- Index status rows ---------- */
.idx{ display:flex; justify-content:space-between; align-items:center; padding:.65rem 0; border-bottom:1px solid var(--border); }
.idx:last-child{ border-bottom:none; }
.idx .n{ font-size:13.5px; font-weight:500; }
.idx .d{ font-size:11.5px; color:var(--faint); }

/* ---------- Evaluation ---------- */
.eval-box{ border-radius:14px; padding:.9rem 1rem; border:1px solid var(--border); background:#fff; }
.eval-box.bad{ background:#FBF6F3; border-color:#F3C4BC; } .eval-box.good{ background:var(--success-soft); border-color:#BFE6D1; }
.eval-box .lbl{ font-size:10.5px; letter-spacing:.14em; font-weight:600; color:var(--muted); margin-bottom:.35rem; }
.eval-box .txt{ font-size:13px; line-height:1.55; }
.eval-box code{ font-size:12px; background:#F3F1EC; padding:.1rem .35rem; border-radius:5px; }
.eval-row{ display:grid; grid-template-columns:150px 1fr; gap:.8rem; padding:.55rem 0; border-bottom:1px solid var(--border); font-size:13px; }
.eval-row:last-child{ border-bottom:none; }
.eval-row .k{ color:var(--muted); font-weight:500; }
.note{ font-size:12.5px; color:var(--success); background:var(--success-soft); border:1px solid #BFE6D1; border-radius:12px; padding:.6rem .9rem; }

/* ---------- Responsive ---------- */
@media (max-width: 900px){
  .block-container{ padding:1.4rem 1.1rem 3rem 1.1rem !important; }
  .sh-title{ font-size:22px; }
  .msg .bubble{ max-width:92%; }
}

/* ---------- UI correction pass: stable widget layout ---------- */
[data-testid="stSidebar"] > div:first-child{ padding-top:1.55rem; }
.sh-section{ margin:1.15rem .5rem .55rem .5rem; line-height:1.1; }
/* Extra breathing room between the "WORKFLOW" heading and the first nav button. */
.sh-section.workflow-section{ margin-bottom:1.3rem; }
[data-testid="stSidebar"] .stButton{ margin:.08rem 0; }
[data-testid="stSidebar"] .stButton > button{ min-height:36px; }

/* Streamlit primary-button text must remain visible against the purple surface. */
.stButton > button[kind="primary"] p,
[data-testid="stButton"] button[kind="primary"] p,
.stButton > button[kind="primary"] span{ color:#fff !important; }
.stButton > button p{ color:inherit !important; }

/* Real uploader only: the previous fake HTML dropzone has been removed. */
.upload-heading{ text-align:center; margin:.2rem 0 .55rem; }
.upload-icon{ width:48px; height:48px; border-radius:14px; display:grid; place-items:center; margin:0 auto .55rem; background:var(--accent-soft); color:var(--accent); font-size:27px; font-weight:700; border:1px solid var(--accent-border); }
.upload-title{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:16px; }
.upload-sub{ color:var(--muted); font-size:12px; margin-top:.2rem; }
[data-testid="stFileUploader"]{ margin:.25rem 0 .6rem; }
[data-testid="stFileUploaderDropzone"]{ min-height:118px !important; display:flex; align-items:center; justify-content:center; padding:1rem !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{ text-align:center; }
.upload-status{ min-height:20px; text-align:center; margin:.15rem 0 .7rem; font-size:12.5px; color:var(--muted); }
.upload-status.muted{ color:var(--faint); }

/* Page 1 profile */
.profile-card{ background:#fff; border:1px solid var(--border); border-radius:16px; padding:1.1rem 1.25rem; box-shadow:var(--shadow); margin:1rem 0; }
.profile-layout{ display:grid; grid-template-columns:minmax(0,2.3fr) minmax(190px,1fr); gap:2rem; align-items:start; }
.profile-main{ display:flex; gap:1rem; align-items:flex-start; }
.profile-text{ min-width:0; }
.profile-name{ font-family:'Space Grotesk',sans-serif; font-size:19px; font-weight:700; }
.profile-role{ color:var(--accent); font-size:13px; font-weight:600; margin:.12rem 0 .35rem; }
.profile-skills{ margin-top:.55rem; }
.profile-checks{ padding-left:1rem; border-left:1px solid var(--border); }
.profile-check-title{ color:var(--muted); font-size:12px; font-weight:600; margin-bottom:.45rem; }
.tab-panel,.summary-panel{ background:#fff; border:1px solid var(--border); border-top:none; border-radius:0 0 14px 14px; padding:1rem; }
.sub-card{ background:var(--card-soft); border:1px solid var(--border); border-radius:12px; padding:.85rem 1rem; margin:.55rem 0; }
.sub-card-head{ display:flex; justify-content:space-between; gap:.75rem; align-items:center; }
.sub-card-meta,.sub-card-muted{ color:var(--muted); font-size:12.5px; margin-top:.2rem; }
.sub-card p{ color:var(--muted); font-size:13px; line-height:1.55; margin:.35rem 0 .55rem; }
.sub-list{ margin:.4rem 0 0 1rem; color:var(--muted); font-size:13px; line-height:1.55; }
.project-card{ min-height:150px; }
.next-row-right{ text-align:right; }

/* Page 2 */
.section-head{ display:flex; align-items:center; justify-content:space-between; gap:1rem; margin:1.1rem 0 .6rem; font-family:'Space Grotesk',sans-serif; font-size:15px; font-weight:600; }
.section-note{ font-family:'Inter',sans-serif; font-size:12px; color:var(--muted); font-weight:400; }
.results-head{ margin-top:1.2rem; }
.jobs-head{ margin-top:1.15rem; }
.role-card{ min-height:108px; height:108px; display:flex; gap:.7rem; align-items:flex-start; padding:.8rem .85rem; }
.role-card .role-rank{ width:25px; height:25px; border-radius:8px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; flex:none; font-size:11px; font-weight:700; }
.role-card .role-body{ min-width:0; display:flex; flex-direction:column; min-height:100%; }
.role-card .r{ margin-top:auto; line-height:1.35; }
.role-card + div[data-testid="stButton"]{ margin-bottom:.35rem; }
.job-card{ padding:1rem 1.1rem; margin-bottom:.35rem; }
.job-card-grid{ display:grid; grid-template-columns:34px minmax(0,1fr) 120px; gap:.85rem; align-items:start; }
.job-score{ text-align:right; padding-top:.05rem; }
.job-chips{ margin-top:.5rem; }
.job-missing{ font-size:11.5px; color:var(--warn); font-weight:600; margin-top:.1rem; }
.job-details{ background:var(--card-soft); border:1px solid var(--border); border-radius:12px; padding:.85rem 1rem; margin:.35rem 0 .8rem 2.5rem; font-size:12.5px; line-height:1.55; color:var(--muted); }
.job-details p{ margin:.6rem 0; color:var(--text); }
.job-details a{ color:var(--accent); font-weight:600; text-decoration:none; }

/* Page 3 */
.target-job-card,.content-card,.soft-card{ background:#fff; border:1px solid var(--border); border-radius:16px; box-shadow:var(--shadow); }
.target-job-card{ padding:1rem 1.1rem; min-height:88px; }
.eyebrow{ font-size:10px; letter-spacing:.16em; color:var(--muted); font-weight:600; }
.target-title{ font-family:'Space Grotesk',sans-serif; font-size:17px; font-weight:700; margin:.15rem 0; }
.target-meta{ color:var(--muted); font-size:12.5px; }
.content-card{ padding:1rem 1.1rem; margin:0 0 1rem; }
.soft-card{ background:var(--card-soft); }
.card-heading{ display:flex; align-items:center; gap:.5rem; font-family:'Space Grotesk',sans-serif; font-size:15px; font-weight:600; margin-bottom:.75rem; }
.readiness-body{ display:flex; align-items:center; gap:1.1rem; }
.readiness-body .ring{ flex:none; margin:0; }
.readiness-copy,.body-copy{ color:var(--muted); font-size:13px; line-height:1.6; }
.priority-row{ display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:.45rem 0; }
.summary-box{ background:var(--card-soft); border:1px solid var(--border); border-radius:12px; padding:.9rem 1rem; font-size:13.5px; line-height:1.7; }
.copy-note{ color:var(--success); font-size:12px; margin:-.55rem 0 .6rem; }
.bullet-improvement{ display:grid; grid-template-columns:28px minmax(0,1fr) 30px minmax(0,1fr); gap:.7rem; align-items:stretch; margin:.7rem 0 1rem; }
.bullet-index{ width:28px; height:28px; border-radius:9px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; font-weight:700; font-size:12px; }
.bullet-improvement .why-box{ grid-column:2 / 5; margin:0; }
.ba-card{ height:auto; min-height:96px; }
.ba-arrow{ align-self:center; padding-top:0; }
.rec{ margin-bottom:.55rem; }

/* Page 4: no nested Streamlit widgets inside raw HTML cards. */
.chat-panel{ min-height:420px; max-height:660px; overflow-y:auto; background:#fff; border:1px solid var(--border); border-radius:16px; box-shadow:var(--shadow); padding:1rem; }
.chat-empty{ min-height:380px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; color:var(--muted); }
.chat-empty-icon{ width:44px; height:44px; border-radius:12px; display:grid; place-items:center; background:var(--accent-soft); color:var(--accent); font-size:20px; margin-bottom:.7rem; }
.chat-empty-title{ font-family:'Space Grotesk',sans-serif; font-weight:600; color:var(--text); }
.chat-empty-sub{ font-size:12.5px; margin-top:.2rem; }
.chat-panel .msg{ width:100%; }
.chat-panel .msg.user{ justify-content:flex-end; }
.chat-panel .msg.bot{ justify-content:flex-start; }
.chat-panel .msg .bubble{ max-width:82%; }
.side-section-title{ background:#fff; border:1px solid var(--border); border-radius:14px; padding:.85rem 1rem; font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:15px; margin-bottom:.6rem; box-shadow:var(--shadow); }
.sources-panel{ background:#fff; border:1px solid var(--border); border-radius:16px; box-shadow:var(--shadow); padding:.2rem .7rem .7rem; }
.sources-panel .side-section-title{ border:none; box-shadow:none; padding:.75rem .35rem .55rem; margin:0; }
.sources-empty{ color:var(--muted); font-size:12.5px; line-height:1.5; padding:.3rem .35rem .6rem; }
.sources-empty.warning{ color:var(--warn); }
.mentor-pipeline{ margin-top:1rem; }

@media (max-width:900px){
  .profile-layout{ grid-template-columns:1fr; gap:1rem; }
  .profile-checks{ border-left:none; border-top:1px solid var(--border); padding:1rem 0 0; }
  .job-card-grid{ grid-template-columns:30px minmax(0,1fr); }
  .job-score{ grid-column:2; text-align:left; }
  .bullet-improvement{ grid-template-columns:28px 1fr; }
  .bullet-improvement .ba-arrow{ display:none; }
  .bullet-improvement .why-box{ grid-column:2; }
}


/* ---------- Final UI refinement pass ---------- */
.search-help{ color:var(--faint); font-size:11.5px; margin:-.85rem 0 .35rem .15rem; }
[data-testid="stSelectbox"] > div > div{ border-radius:12px !important; border:1px solid var(--border-strong) !important; background:#fff !important; min-height:40px; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div{ border-radius:12px !important; }
[data-testid="stSelectbox"] input{ font-size:14px !important; }
.project-hero{ text-align:center; margin:-.25rem 0 1.15rem; padding:.35rem 1rem .1rem; }
.project-hero-title{ font-family:'Space Grotesk',sans-serif; color:var(--text); font-size:18px; font-weight:700; }
.project-hero-copy{ max-width:760px; margin:.3rem auto 0; color:var(--muted); font-size:12.5px; line-height:1.55; }
.inline-button-spacer{ height:1.05rem; }
.next-action-gap{ height:.65rem; }
.cv-section-head{ margin-top:1rem; }
.rewrite-row{ display:grid; grid-template-columns:30px minmax(0,1fr); gap:.7rem; margin:.1rem 0 1rem; }
.rewrite-index{ width:28px; height:28px; border-radius:9px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; font-weight:700; font-size:12px; }
.rewrite-main{ min-width:0; }
.rewrite-title{ font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:14px; margin-bottom:.45rem; }
.rewrite-grid{ display:grid; grid-template-columns:1fr 1fr; gap:.75rem; }
.skills-followup{ margin-top:.55rem; }
.issue-row{ display:grid; grid-template-columns:auto minmax(0,1fr); gap:.55rem; align-items:start; margin:.55rem 0; padding:.55rem .65rem; border:1px solid var(--border); border-radius:10px; background:var(--card-soft); }
.issue-copy{ color:var(--muted); font-size:12.5px; line-height:1.5; }
.issue-copy b{ color:var(--text); display:block; margin-bottom:.12rem; }
.mentor-send-spacer{ height:1.05rem; }
.mentor-footer{ margin:1.1rem 0 .6rem; padding:1.3rem 1.5rem; border:1px solid var(--border); border-radius:16px; background:var(--card-soft); text-align:center; box-shadow:var(--shadow); }
.mentor-footer-title{ font-family:'Space Grotesk',sans-serif; font-size:16px; font-weight:700; color:var(--text); }
.mentor-footer-copy{ max-width:760px; margin:.35rem auto 0; color:var(--muted); font-size:12.5px; line-height:1.55; }
.mentor-thanks{ margin-top:.6rem; color:var(--accent); font-size:12.5px; font-weight:600; }
@media(max-width:900px){ .rewrite-grid{ grid-template-columns:1fr; } }


/* ---------- Final UI hierarchy pass ---------- */
/* The application canvas remains warm peach. Cards are white; nested controls
   use a subtly darker white so the hierarchy is visible without changing the page canvas. */

/* NOTE: [data-testid="stVerticalBlockBorderWrapper"] does not exist in the
   installed Streamlit build (1.63) — that wrapper testid was removed in a
   frontend refactor, so any rule gated on it matches nothing. Every bordered
   st.container() in this app is given an explicit key=, which Streamlit adds
   as an "st-key-<key>" CSS class directly on the [data-testid="stVerticalBlock"]
   element — see job_match.py and cv_improvement.py, which style their specific
   cards by that class. This generic rule is kept only as a harmless fallback
   in case a future Streamlit version reintroduces a dedicated wrapper testid;
   it intentionally does not try to guess a class name here, since guessing
   wrong is what caused the original bug. */
[data-testid="stVerticalBlockBorderWrapper"] {
  background:#FFFFFF !important;
  border:1px solid #171B2B !important;
  border-radius:16px !important;
  box-shadow:none !important;
}
[data-testid="stVerticalBlockBorderWrapper"] .stElementContainer {
  margin-top:0 !important;
  margin-bottom:0 !important;
}

/* Nested widget surfaces: darker white inside the white parent card. */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background:#EAEBEF !important;
  color:var(--text) !important;
  border:1px solid #171B2B !important;
  border-radius:12px !important;
}

[data-testid="stTextInput"] > div > div,
[data-testid="stTextArea"] > div > div {
  background:transparent !important;
  border:none !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color:var(--accent) !important;
  box-shadow:0 0 0 3px rgba(79,70,229,.12) !important;
}

/* Secondary buttons are near-white; primary actions remain purple. */
.stButton > button {
  background:#EAEBEF !important;
  color:var(--text) !important;
  border:1px solid #171B2B !important;
  box-shadow:none !important;
}
.stButton > button:hover {
  background:#FFFFFF !important;
  border-color:var(--accent) !important;
  color:var(--accent) !important;
}
.stButton > button[kind="primary"] {
  background:var(--accent) !important;
  color:#FFFFFF !important;
  border-color:var(--accent) !important;
}

/* Job Match: white outer card, slightly darker white textarea. */
.job-match-jd-shell {
  background:#FFFFFF !important;
  border:1px solid #171B2B !important;
  border-radius:16px !important;
  padding:1.05rem 1.05rem !important;
}
[data-testid="stTextArea"] textarea {
  background:#EAEBEF !important;
}

/* CV Improvement nested tiles. */
.cv-card-content .sh-metric { padding:.85rem .95rem !important; min-height:86px !important; }
.cv-card-content .summary-box { padding:.85rem .95rem !important; }
.cv-card-content .ba-card { padding:.85rem .95rem !important; }
.cv-card-content .why-box { padding:.65rem .8rem !important; }
.cv-card-content .issue-row { padding:.65rem .75rem !important; }
.cv-card-content .rec { padding:.8rem .9rem !important; }
.cv-card-content .rewrite-grid {
  display:grid !important;
  grid-template-columns:1fr !important;
  gap:.7rem !important;
}
.cv-two-card-grid [data-testid="column"] { min-width:0 !important; }
.cv-gap { height:1rem; }

/* The old global `[data-testid="stForm"]` composer rules that used to live
   here have been removed: mentor.py now scopes its own composer styling
   under `.mentor-composer-shell` (see MENTOR_PAGE_CSS there), but this
   block was never deleted - it kept forcing `width:42px` onto the submit
   button of EVERY st.form on EVERY page (including the Job Match "Send"
   button), which is why "Send" was wrapping into individual stacked
   letters inside a tiny box. */

.mentor-pipeline,
.mentor-footer {
  background:#FFFFFF !important;
  border:1px solid #171B2B !important;
}


/* ---------- v4 correction: restore original sidebar styling ---------- */
[data-testid="stSidebar"] .stButton > button {
  width:100% !important;
  justify-content:flex-start !important;
  border-radius:10px !important;
  border:1px solid transparent !important;
  background:transparent !important;
  color:#C9CDDA !important;
  font-weight:500 !important;
  font-size:13.5px !important;
  padding:.5rem .8rem !important;
  min-height:38px !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background:var(--navy-2) !important;
  color:#FFFFFF !important;
  border-color:var(--navy-border) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background:var(--accent) !important;
  color:#FFFFFF !important;
  border-color:var(--accent) !important;
  box-shadow:0 6px 16px -8px rgba(79,70,229,.8) !important;
}
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span {
  color:inherit !important;
}

/* ---------- v4 correction: uploader remains blue/light-blue, but gains separation shadow ---------- */
[data-testid="stFileUploaderDropzone"] {
  box-shadow:0 10px 26px -14px rgba(31,41,55,.38),
             0 2px 7px rgba(31,41,55,.10) !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
  box-shadow:0 12px 30px -14px rgba(31,41,55,.42),
             0 3px 9px rgba(31,41,55,.12) !important;
}

/* Do not apply main-page button styling to sidebar controls. */
[data-testid="stSidebar"] .stButton > button {
  isolation:isolate;
}


/* ---------- CV Improvement: strict white-card hierarchy ---------- */
/*
  Each CV section is an explicit keyed st.container().  Streamlit 1.63
  exposes the key as an `st-key-...` class on the rendered vertical block.
  Scope the white-card rules to those keys instead of relying on the
  version-sensitive generic border-wrapper testid.
*/
.st-key-cv_card_target_job,
.st-key-cv_card_ats_score,
.st-key-cv_card_matched_skills,
.st-key-cv_card_missing_skills,
.st-key-cv_card_soft_skills,
.st-key-cv_card_summary,
.st-key-cv_card_skills_section,
.st-key-cv_card_rewrite_experience,
.st-key-cv_card_rewrite_project,
.st-key-cv_card_rewrite_certification,
.st-key-cv_card_rewrite_achievement,
.st-key-cv_card_rewrite_bullet,
.st-key-cv_card_recommendations{
  background:#FFFFFF !important;
  border:1px solid #171B2B !important;
  border-radius:16px !important;
  box-shadow:0 1px 2px rgba(20,20,40,.04),
             0 8px 22px -14px rgba(20,20,40,.14) !important;
  padding:1.05rem 1.05rem !important;
  box-sizing:border-box !important;
}

/* Streamlit inserts descendant layout blocks. Keep those transparent so
   the actual keyed card remains the visible white surface. */
.st-key-cv_card_target_job [data-testid="stVerticalBlock"],
.st-key-cv_card_ats_score [data-testid="stVerticalBlock"],
.st-key-cv_card_matched_skills [data-testid="stVerticalBlock"],
.st-key-cv_card_missing_skills [data-testid="stVerticalBlock"],
.st-key-cv_card_soft_skills [data-testid="stVerticalBlock"],
.st-key-cv_card_summary [data-testid="stVerticalBlock"],
.st-key-cv_card_skills_section [data-testid="stVerticalBlock"],
.st-key-cv_card_rewrite_experience [data-testid="stVerticalBlock"],
.st-key-cv_card_rewrite_project [data-testid="stVerticalBlock"],
.st-key-cv_card_rewrite_certification [data-testid="stVerticalBlock"],
.st-key-cv_card_rewrite_achievement [data-testid="stVerticalBlock"],
.st-key-cv_card_rewrite_bullet [data-testid="stVerticalBlock"],
.st-key-cv_card_recommendations [data-testid="stVerticalBlock"]{
  background:transparent !important;
}

/* All ordinary content inside CV parent cards sits on white. */
.st-key-cv_card_target_job,
.st-key-cv_card_target_job > div,
.st-key-cv_card_ats_score,
.st-key-cv_card_ats_score > div,
.st-key-cv_card_matched_skills,
.st-key-cv_card_matched_skills > div,
.st-key-cv_card_missing_skills,
.st-key-cv_card_missing_skills > div,
.st-key-cv_card_soft_skills,
.st-key-cv_card_soft_skills > div,
.st-key-cv_card_summary,
.st-key-cv_card_summary > div,
.st-key-cv_card_skills_section,
.st-key-cv_card_skills_section > div,
.st-key-cv_card_rewrite_experience,
.st-key-cv_card_rewrite_experience > div,
.st-key-cv_card_rewrite_project,
.st-key-cv_card_rewrite_project > div,
.st-key-cv_card_rewrite_certification,
.st-key-cv_card_rewrite_certification > div,
.st-key-cv_card_rewrite_achievement,
.st-key-cv_card_rewrite_achievement > div,
.st-key-cv_card_rewrite_bullet,
.st-key-cv_card_rewrite_bullet > div,
.st-key-cv_card_recommendations,
.st-key-cv_card_recommendations > div{
  background-color:#FFFFFF !important;
}

/* Intentional nested surfaces: slightly darker than the white parent card. */
.st-key-cv_card_summary .summary-box,
.st-key-cv_card_summary .ba-card,
.st-key-cv_card_skills_section .ba-card,
.st-key-cv_card_soft_skills .issue-row,
.st-key-cv_card_missing_skills .sh-metric,
.st-key-cv_card_rewrite_experience .ba-card,
.st-key-cv_card_rewrite_project .ba-card,
.st-key-cv_card_rewrite_certification .ba-card,
.st-key-cv_card_rewrite_achievement .ba-card,
.st-key-cv_card_rewrite_bullet .ba-card,
.st-key-cv_card_recommendations .rec,
.st-key-cv_card_recommendations .issue-row,
.st-key-cv_card_summary .why-box,
.st-key-cv_card_skills_section .why-box,
.st-key-cv_card_rewrite_experience .why-box,
.st-key-cv_card_rewrite_project .why-box,
.st-key-cv_card_rewrite_certification .why-box,
.st-key-cv_card_rewrite_achievement .why-box,
.st-key-cv_card_rewrite_bullet .why-box{
  background:#F1F2F4 !important;
  border:1px solid #9EA3AE !important;
  box-shadow:none !important;
}

/* AFTER panels remain distinct but stay in the white family rather than
   turning green/blue. */
.st-key-cv_card_summary .ba-card.after,
.st-key-cv_card_skills_section .ba-card.after,
.st-key-cv_card_rewrite_experience .ba-card.after,
.st-key-cv_card_rewrite_project .ba-card.after,
.st-key-cv_card_rewrite_certification .ba-card.after,
.st-key-cv_card_rewrite_achievement .ba-card.after,
.st-key-cv_card_rewrite_bullet .ba-card.after{
  background:#F6F7F8 !important;
  border-color:#A9B1BD !important;
}

/* Balanced vertical rhythm inside every CV card. */
.st-key-cv_card_target_job,
.st-key-cv_card_ats_score,
.st-key-cv_card_matched_skills,
.st-key-cv_card_missing_skills,
.st-key-cv_card_soft_skills,
.st-key-cv_card_summary,
.st-key-cv_card_skills_section,
.st-key-cv_card_rewrite_experience,
.st-key-cv_card_rewrite_project,
.st-key-cv_card_rewrite_certification,
.st-key-cv_card_rewrite_achievement,
.st-key-cv_card_rewrite_bullet,
.st-key-cv_card_recommendations{
  margin-top:0 !important;
  margin-bottom:0 !important;
}

/* ---------- Sidebar: preserve original navy design ---------- */
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]){
  background:transparent !important;
  color:#C9CDDA !important;
  border-color:transparent !important;
}
[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover{
  background:var(--navy-2) !important;
  color:#FFFFFF !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]{
  background:var(--accent) !important;
  color:#FFFFFF !important;
  border-color:var(--accent) !important;
}

/* The requested extra breathing room below WORKFLOW. */
.sh-section.workflow-section{
  margin-bottom:1.55rem !important;
}

/* Mentor composer: white outer box with a black border (was picking up
   the page's peach background because this container had no explicit
   fill). The actual input surface inside it is left to inherit the same
   darker-white shade used for every other nested surface on this page
   (see the generic [data-testid="stTextInput"] input rule above), the
   same white-outer / darker-white-inner pattern already used for the
   Job Match JD box. */
.st-key-mentor_input_bar{
  background:#FFFFFF !important;
  border:1px solid #171B2B !important;
  border-radius:16px !important;
  box-shadow:0 6px 20px -12px rgba(20,20,40,.18), 0 2px 6px rgba(20,20,40,.06) !important;
}
.st-key-mentor_input_bar [data-testid="stVerticalBlock"]{
  background:transparent !important;
}

/* Suggested Questions: let the full question wrap onto two or three
   lines instead of being clipped to a single truncated line. */
[class*="st-key-mentor_suggestion_"] button{
  white-space:normal !important;
  height:auto !important;
  min-height:44px !important;
  line-height:1.35 !important;
  text-align:left !important;
  padding:.55rem .75rem !important;
}
[class*="st-key-mentor_suggestion_"] button p{
  white-space:normal !important;
  text-align:left !important;
  margin:0 !important;
}

</style>
"""


def inject_css() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)