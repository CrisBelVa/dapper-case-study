# ui.py  (repository root)
import streamlit as st

GOOGLE_MATERIAL_CSS = """
<style>
:root {
  --g-primary:#1A73E8; --g-green:#34A853; --g-yellow:#FBBC05; --g-red:#EA4335;
  --g-text:#202124; --g-muted:#5F6368; --g-bg:#FFFFFF; --g-bg2:#F8F9FA; --g-border:#E0E0E0;
  --g-shadow:0 1px 2px rgba(0,0,0,0.06), 0 2px 6px rgba(0,0,0,0.06);
  --radius:12px; --pad:16px;
}
.block-container { padding-top: 1.2rem; }
h1,h2,h3 { color: var(--g-text); letter-spacing: -0.2px; }
.g-card { background:var(--g-bg); border:1px solid var(--g-border); border-radius:var(--radius);
         padding:var(--pad); box-shadow:var(--g-shadow); margin-bottom:12px; }
.kpi { display:inline-flex; align-items:center; gap:8px; padding:10px 14px; border-radius:999px;
       border:1px solid var(--g-border); background:var(--g-bg); box-shadow:0 1px 2px rgba(0,0,0,0.04);
       font-weight:600; color:var(--g-text); }
.kpi .dot { width:10px; height:10px; border-radius:50%; background:var(--g-primary); }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { background:var(--g-bg); border:1px solid var(--g-border); border-radius:999px;
                               padding:8px 14px; color:var(--g-muted); }
.stTabs [aria-selected="true"] { border-color:var(--g-primary)!important; color:var(--g-primary)!important; }
.stButton > button { border-radius:8px!important; border:1px solid var(--g-border)!important;
                     box-shadow:var(--g-shadow)!important; }
.stAlert { border-radius: var(--radius); }
</style>
"""

def inject_google_css():
    st.markdown(GOOGLE_MATERIAL_CSS, unsafe_allow_html=True)

def card_start(title: str, subtitle: str | None = None):
    st.markdown(
        f'<div class="g-card"><h3>{title}</h3>'
        + (f'<p style="color:#5F6368;margin-top:-6px;">{subtitle}</p>' if subtitle else ''),
        unsafe_allow_html=True,
    )

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)

def kpi_chip(label: str, value: str, tone: str = "primary"):
    color = {
        "primary": "var(--g-primary)",
        "green": "var(--g-green)",
        "red": "var(--g-red)",
        "yellow": "var(--g-yellow)",
    }.get(tone, "var(--g-primary)")
    st.markdown(
        f'<span class="kpi"><span class="dot" style="background:{color};"></span>{label}: {value}</span>',
        unsafe_allow_html=True,
    )
