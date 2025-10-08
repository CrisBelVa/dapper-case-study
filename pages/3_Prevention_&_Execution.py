import streamlit as st
import pandas as pd
import altair as alt
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
st.set_page_config(page_title="Part X – <Page Name>", layout="wide")  # or "centered" where you want

from ui import card_start, card_end, kpi_chip, inject_google_css



st.title("Part 3 – Prevention & Execution")

# =======================
# 1) BOT MITIGATION FRAMEWORK
# =======================
card_start("1. 🛡️ Bot Mitigation Framework", "Protect performance data and stop fake sessions/conversions")

st.markdown("""
**Multi-layered protection to ensure only real users impact performance data:**

**✅ GA4 + GTM Validation (Engagement-Based Firing)**
- Minimum session time (10–15s)
- Scroll depth or multiple pageviews
- Exclusion of free/invalid email domains
- Honeypot or hidden field triggers

**✅ Form Hardening**
- Multi-step forms (e.g. Growform)
- Honeypots (hidden fields)
- reCAPTCHA v3 or hCaptcha scoring

**✅ Ad Platform Controls**
- “People in location” (not “interested in”)
- Frequency caps
- Exclude Display Network & Search Partners for lead gen

**✅ Click Fraud & Traffic Protection Tools**
- Lunio / TrafficGuard for real-time blocking
- DataDome for full-site defense

**✅ Ongoing Monitoring**
- GA4 anomaly detection
- IP/device blacklisting
- Heatmap analysis for non-human behavior
""")

card_end()

# =======================
# 2) EXECUTION PLAN – TIMELINE
# =======================
card_start("2. 📊 Execution Plan – Timeline", "Strategy remains the same — pacing and validation change")

st.markdown("""
We do **not** change the paid strategy — research confirms real US market potential.  
Instead, we **control the rollout** to ensure only clean, high-quality data informs scaling.
""")


timeline_data = pd.DataFrame([
    {"Phase": "Phase 1 — Validate", "Start": 0, "End": 2, "Label": "Weeks 1–2"},
    {"Phase": "Phase 2 — Scale Slowly", "Start": 2, "End": 4, "Label": "Weeks 3–4"},
    {"Phase": "Phase 3 — Expand", "Start": 4, "End": 8, "Label": "Month 2+"},
])

timeline_chart = alt.Chart(timeline_data).mark_bar().encode(
    x=alt.X("Start:Q", title=None),
    x2="End:Q",
    y=alt.Y("Phase:N", title=None),
    tooltip=["Phase", "Label"]
).properties(
    width=700,
    height=200
)

st.altair_chart(timeline_chart, use_container_width=True)


# ---- Horizontal timeline (Phase 1 → Phase 2 → Phase 3)
TIMELINE_CSS = """
<style>
.timeline {
  margin-top: .5rem; margin-bottom: 1rem;
  padding: 16px; border: 1px solid var(--g-border);
  border-radius: var(--radius); background: var(--g-bg); box-shadow: var(--g-shadow);
}
.timeline-bar {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;
  align-items: center; margin: 8px 0 10px 0;
}
.tseg {
  height: 12px; border-radius: 999px; background: #e9ecef; position: relative;
}
.tseg.phase1 { background: var(--g-primary); }
.tseg.phase2 { background: linear-gradient(90deg, var(--g-primary) 0 50%, #e9ecef 50%); }
.tseg.phase3 { background: linear-gradient(90deg, #e9ecef 0 70%, var(--g-primary) 70%); }
.timeline-labels {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;
  font-size: 0.92rem; color: var(--g-text);
}
.timeline-labels .lbl {
  display: flex; flex-direction: column; gap: 4px;
  padding: 8px 10px; border: 1px solid var(--g-border);
  border-radius: 10px; background: var(--g-bg2);
}
.timeline-labels .ttl { font-weight: 600; }
.timeline-note { color: var(--g-muted); font-size: .9rem; margin-top: 4px; }
</style>
"""
st.markdown(TIMELINE_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="timeline">
  <div class="timeline-bar">
    <div class="tseg phase1" title="Weeks 1–2"></div>
    <div class="tseg phase2" title="Weeks 3–4"></div>
    <div class="tseg phase3" title="Month 2+"></div>
  </div>
  <div class="timeline-labels">
    <div class="lbl">
      <div class="ttl">Phase 1 — Validate</div>
      <div>Weeks 1–2 • Strict monitoring, bot checks, lead QA</div>
    </div>
    <div class="lbl">
      <div class="ttl">Phase 2 — Scale Slowly</div>
      <div>Weeks 3–4 • Increase budget on proven campaigns</div>
    </div>
    <div class="lbl">
      <div class="ttl">Phase 3 — Expand</div>
      <div>Month 2+ • Add YouTube & broader awareness once quality holds</div>
    </div>
  </div>
  <div class="timeline-note">We keep the paid strategy unchanged; we adjust pacing & monitoring to ensure clean, human demand before scaling.</div>
</div>
""", unsafe_allow_html=True)

card_end()
