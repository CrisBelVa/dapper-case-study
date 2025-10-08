# pages/2_Paid_Strategy.py
import re
import streamlit as st
import pandas as pd
import altair as alt

from app import card_start, card_end, kpi_chip, inject_google_css

# after st.set_page_config(...)
inject_google_css()


st.set_page_config(page_title="Part 2 – Paid Marketing Strategy", layout="wide")
st.title("Part 2 – Paid Marketing Strategy (Behavior Change Launch)")

# -----------------------------
# Helpers for estimation
# -----------------------------
def _mid_range_num(txt: str) -> float | None:
    """Return midpoint of a range like '€45–65' or '0.8–1.2%' (as numeric, % => decimal). '—' -> None."""
    if txt is None: return None
    s = str(txt).strip()
    if s in ("—", "-", ""): return None
    s = s.replace("€", "").replace(",", "").replace(" ", "")
    # Extract percents, note % handling after numbers found
    pct = s.endswith("%")
    s = s.replace("%", "")
    parts = re.split(r"[–-]", s)  # split on en-dash or hyphen
    try:
        if len(parts) == 1:
            val = float(parts[0])
        else:
            val = (float(parts[0]) + float(parts[1])) / 2.0
        if pct:
            val = val / 100.0
        return val
    except Exception:
        return None

def estimate_row_impr_clicks(budget_eur: float, cpm_txt: str, cpc_txt: str, ctr_txt: str) -> tuple[float, float]:
    """
    Estimate impressions & clicks for a single line using whatever is available:
    - If CPM present -> Impr = budget / (CPM/1000); if CTR present -> Clicks = Impr * CTR
    - Else if CPC present -> Clicks = budget / CPC; if CTR present -> Impr = Clicks / CTR
    - Else fallback zeros
    """
    cpm = _mid_range_num(cpm_txt)
    cpc = _mid_range_num(cpc_txt)
    ctr = _mid_range_num(ctr_txt)

    impr = 0.0
    clicks = 0.0

    if cpm:  # we can get impressions
        impr = budget_eur / (cpm / 1000.0)
        if ctr:
            clicks = impr * ctr
    elif cpc:  # no CPM, but CPC given
        clicks = budget_eur / cpc
        if ctr and ctr > 0:
            impr = clicks / ctr
    return impr, clicks

def donut_chart(df, field, value_field, title):
    chart = alt.Chart(df).mark_arc(innerRadius=70).encode(
        theta=alt.Theta(f"{value_field}:Q"),
        color=alt.Color(f"{field}:N", legend=alt.Legend(title=field)),
        tooltip=[field, value_field]
    ).properties(height=300, title=title)
    return chart

# -----------------------------
# 1) PAID MEDIA CHANNEL SCENARIOS
# -----------------------------
card_start("1) Budget Overview by Channel & Funnel", "Two investment scenarios with clear funnel roles")

# IMPORTANT: Corrections applied
# - LinkedIn Retargeting moved to MOFU (engagement/capture)
# - BOFU is Google Search (Exact/Branded/Competitor) to hit high intent

scenario_15k = pd.DataFrame([
    {"Funnel": "TOFU (Create Demand)", "Channel": "LinkedIn (Awareness)", "Budget": 6000},
    {"Funnel": "TOFU (Create Demand)", "Channel": "YouTube (Awareness)",   "Budget": 2000},

    {"Funnel": "MOFU (Capture/Engage)", "Channel": "Google Search – Text Ads (Generic)", "Budget": 3000},
    {"Funnel": "MOFU (Capture/Engage)", "Channel": "Google Search – RLSA (Retargeting)", "Budget": 1000},
    {"Funnel": "MOFU (Capture/Engage)", "Channel": "LinkedIn (Retargeting: Text/Conversation)", "Budget": 2000},

    {"Funnel": "BOFU (Convert High Intent)", "Channel": "Google Search – Exact/Branded/Competitor", "Budget": 1000},
])

scenario_30k = pd.DataFrame([
    {"Funnel": "TOFU (Create Demand)", "Channel": "LinkedIn (Awareness)", "Budget": 12000},
    {"Funnel": "TOFU (Create Demand)", "Channel": "YouTube (Awareness)",   "Budget": 4000},

    {"Funnel": "MOFU (Capture/Engage)", "Channel": "Google Search – Text Ads (Generic)", "Budget": 6000},
    {"Funnel": "MOFU (Capture/Engage)", "Channel": "Google Search – RLSA (Retargeting)", "Budget": 2000},
    {"Funnel": "MOFU (Capture/Engage)", "Channel": "LinkedIn (Retargeting: Text/Conversation)", "Budget": 4000},

    {"Funnel": "BOFU (Convert High Intent)", "Channel": "Google Search – Exact/Branded/Competitor", "Budget": 2000},
])

def with_pct(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    total = out["Budget"].sum()
    out["%Budget"] = (out["Budget"] / total * 100).round(1)
    return out

scenario_map = {
    "€15K / month": with_pct(scenario_15k),
    "€30K / month": with_pct(scenario_30k),
}

sel = st.radio("Select scenario", list(scenario_map.keys()), horizontal=True)
df_sel = scenario_map[sel]
total_budget = int(df_sel["Budget"].sum())

# Dynamic ratio by funnel
ratio_df = df_sel.groupby("Funnel", as_index=False)["Budget"].sum()
ratio_df["Pct"] = (ratio_df["Budget"] / ratio_df["Budget"].sum() * 100).round(0)
ratio_str = " • ".join([f"{r['Funnel'].split(' ')[0]}: {int(r['Pct'])}%" for _, r in ratio_df.iterrows()])

c1, c2, c3 = st.columns([1,1,1])
with c1: kpi_chip("Total Budget", f"€{total_budget:,}")
with c2: kpi_chip("Create / Capture / Convert", ratio_str, "yellow")
with c3: kpi_chip("Primary Channels", "LinkedIn • Google • YouTube", "green")

st.dataframe(df_sel, use_container_width=True)


# --- NEW: Donut for budget share by channel ---
# Normalize channels to parent (LinkedIn / Google / YouTube)
def parent_channel(name: str) -> str:
    if "LinkedIn" in name: return "LinkedIn"
    if "YouTube" in name: return "YouTube"
    return "Google"

budget_by_channel = (
    df_sel.assign(Parent=df_sel["Channel"].map(parent_channel))
         .groupby("Parent", as_index=False)["Budget"].sum()
)
st.altair_chart(
    donut_chart(budget_by_channel, "Parent", "Budget", "Budget Share by Channel"),
    use_container_width=True
)

st.caption("**Changes applied:** LinkedIn retargeting now **MOFU**; **BOFU** focuses on **Search Exact/Branded** for highest intent conversion.")

card_end()

# -----------------------------
# 2) OVERVIEW – CAMPAIGN TYPES (formats split + Google retargeting)
# -----------------------------
card_start("2) Campaign Type Overview", "Formats, segmentation, and estimated delivery metrics")

overview_df = pd.DataFrame([
    # TOFU
    {"Channel":"LinkedIn","Funnel Stage":"TOFU","Campaign Type":"LinkedIn Awareness","Format / Ad Type":"Thought Leadership Posts",
     "Segmentation":"Job Titles + Industry + Company Size (1k–10k, 10k+)",
     "Budget":3000,"CPC":"€6–9","CPM":"€40–60","CTR":"0.6–1.0%"},
    {"Channel":"LinkedIn","Funnel Stage":"TOFU","Campaign Type":"LinkedIn Awareness","Format / Ad Type":"Video Ads",
     "Segmentation":"Same as above",
     "Budget":3000,"CPC":"€6–9","CPM":"€45–65","CTR":"0.8–1.2%"},
    {"Channel":"YouTube","Funnel Stage":"TOFU","Campaign Type":"YouTube Awareness","Format / Ad Type":"Shorts / In-stream",
     "Segmentation":"Affinity & professional interests (HR/L&D/Compliance)",
     "Budget":2000,"CPC":"—","CPM":"€10–15","CTR":"0.4–0.7%"},
    # MOFU
    {"Channel":"Google","Funnel Stage":"MOFU","Campaign Type":"Google Search","Format / Ad Type":"Text Ads (Generic)",
     "Segmentation":"KWs: serious games, simulation training, gamified learning",
     "Budget":3000,"CPC":"€3–7","CPM":"—","CTR":"3–5%"},
    {"Channel":"Google","Funnel Stage":"MOFU","Campaign Type":"Google Search (Retargeting)","Format / Ad Type":"RLSA (Search audiences)",
     "Segmentation":"Site visitors + YouTube/LinkedIn engagers",
     "Budget":1000,"CPC":"€3–6","CPM":"—","CTR":"4–6%"},
    {"Channel":"LinkedIn","Funnel Stage":"MOFU","Campaign Type":"LinkedIn Retargeting","Format / Ad Type":"Text/Conversation Ads",
     "Segmentation":"Website visitors & video viewers (90 days)",
     "Budget":2000,"CPC":"€5–8","CPM":"€30–50","CTR":"1.0–1.8%"},
    # BOFU
    {"Channel":"Google","Funnel Stage":"BOFU","Campaign Type":"Google Search","Format / Ad Type":"Exact/Branded/Competitor",
     "Segmentation":"Exact brand + competitors; high-intent",
     "Budget":1000,"CPC":"€3–6","CPM":"—","CTR":"5–8%"},
])

# Scale budgets for 30k scenario
if "€30K" in sel:
    overview_df = overview_df.copy()
    overview_df["Budget"] = (overview_df["Budget"] * 2).astype(int)

# Estimate impressions & clicks per row
est_rows = []
for _, r in overview_df.iterrows():
    impr, clicks = estimate_row_impr_clicks(
        budget_eur=float(r["Budget"]),
        cpm_txt=r["CPM"],
        cpc_txt=r["CPC"],
        ctr_txt=r["CTR"],
    )
    est_rows.append({"Impressions_est": impr, "Clicks_est": clicks})
est_df = pd.DataFrame(est_rows)
overview_df = pd.concat([overview_df.reset_index(drop=True), est_df], axis=1)

# Human-readable columns
display_df = overview_df.copy()
display_df["Clicks (est)"] = display_df["Clicks_est"].round().astype(int)
display_df["Impressions (est)"] = display_df["Impressions_est"].round().astype(int)
display_df = display_df.drop(columns=["Clicks_est","Impressions_est"])

st.dataframe(display_df, use_container_width=True)
st.caption("Benchmarks are directional (based on LinkedIn screenshots + research). Replace with live platform estimates before launch.")

# --- NEW: Donuts for estimated impressions & clicks by channel ---
by_channel = overview_df.groupby("Channel", as_index=False)[["Impressions_est","Clicks_est","Budget"]].sum()

c1, c2 = st.columns(2)
with c1:
    st.altair_chart(
        donut_chart(by_channel.rename(columns={"Impressions_est":"Impressions"}), "Channel", "Impressions", "Est. Impressions by Channel"),
        use_container_width=True
    )
with c2:
    st.altair_chart(
        donut_chart(by_channel.rename(columns={"Clicks_est":"Clicks"}), "Channel", "Clicks", "Est. Clicks by Channel"),
        use_container_width=True
    )

card_end()

# -----------------------------
# 3) CONTENT FRAMEWORK (formats separated)
# -----------------------------
card_start("3) Content Framework", "Exactly what we need per funnel to prove behavior change")

content_df = pd.DataFrame([
    # TOFU – LinkedIn posts
    {"Funnel Stage":"TOFU","Campaign Type":"LinkedIn Awareness","FORMAT":"Thought Leadership Posts",
     "TARGETING METHOD":"Job Title + Industry + Size (1k–10k, 10k+)","WHAT DO WE NEED FOR TARGETING":"Audience filters • persona list • creative set",
     "CONTENT VISUAL SPECS":"1080×1080 / 1200×628; clean, brand-safe; data point or quote",
     "CONTENT TEXTUAL SPECS":"Hook + insight; 2–3 short lines; no CTA (value only)",
     "CONTENT VIDEO SPECS":"—","AD DESTINATION":"Blog / resource explaining behavior shifts",
     "Links to Visuals":"TBD","KPIs":"Engagement rate, saves, profile visits"},
    # TOFU – LinkedIn video
    {"Funnel Stage":"TOFU","Campaign Type":"LinkedIn Awareness","FORMAT":"Video Ads",
     "TARGETING METHOD":"Same audience as above","WHAT DO WE NEED FOR TARGETING":"Script + edit + captions",
     "CONTENT VISUAL SPECS":"1:1 or 4:5, large captions; product-in-use",
     "CONTENT TEXTUAL SPECS":"Outcome oriented (time-to-competence, fewer errors)","CONTENT VIDEO SPECS":"15–30s; subtitles; first 2s hook",
     "AD DESTINATION":"Landing page: behavior outcomes","Links to Visuals":"TBD","KPIs":"Thru-play, CTR"},
    # TOFU – YouTube
    {"Funnel Stage":"TOFU","Campaign Type":"YouTube Awareness","FORMAT":"Shorts / In-stream",
     "TARGETING METHOD":"Affinity + in-market HR/L&D/Compliance","WHAT DO WE NEED FOR TARGETING":"2 edits (6–15s & 15–30s)",
     "CONTENT VISUAL SPECS":"Vertical/16:9; overlay benefit text","CONTENT TEXTUAL SPECS":"CTA in end card",
     "CONTENT VIDEO SPECS":"6–15s bumper; 15–30s skippable","AD DESTINATION":"Blog or light LP","Links to Visuals":"TBD","KPIs":"VTR, cost per view"},
    # MOFU – Google text (Generic)
    {"Funnel Stage":"MOFU","Campaign Type":"Google Search","FORMAT":"Text Ads (Generic)",
     "TARGETING METHOD":"KWs: serious games, compliance simulation, onboarding game","WHAT DO WE NEED FOR TARGETING":"KW list, negatives, bid caps",
     "CONTENT VISUAL SPECS":"—","CONTENT TEXTUAL SPECS":"Responsive headlines; outcome claims + proof",
     "CONTENT VIDEO SPECS":"—","AD DESTINATION":"LP with case study & ROI figures","Links to Visuals":"—","KPIs":"CTR, CPC, CPL"},
    # MOFU – Google RLSA
    {"Funnel Stage":"MOFU","Campaign Type":"Google Search (Retargeting)","FORMAT":"RLSA",
     "TARGETING METHOD":"Site visitors; YT/LI engagers","WHAT DO WE NEED FOR TARGETING":"GA4 audiences; LI Insight Tag; YT lists",
     "CONTENT VISUAL SPECS":"—","CONTENT TEXTUAL SPECS":"Stronger CTA (book pilot)",
     "CONTENT VIDEO SPECS":"—","AD DESTINATION":"Demo request","Links to Visuals":"—","KPIs":"Conv rate, CPA"},
    # MOFU – LinkedIn Retargeting
    {"Funnel Stage":"MOFU","Campaign Type":"LinkedIn Retargeting","FORMAT":"Text/Conversation Ads",
     "TARGETING METHOD":"Visitors + video viewers + CRM","WHAT DO WE NEED FOR TARGETING":"Sender profile • message tree • UTM tracking",
     "CONTENT VISUAL SPECS":"Message layout; optional GIF","CONTENT TEXTUAL SPECS":"Personal opener + 2 options (demo / case study)",
     "CONTENT VIDEO SPECS":"Optional 10–15s clip","AD DESTINATION":"Demo calendar","Links to Visuals":"TBD","KPIs":"Replies, CTR, demos"},
    # BOFU – Google Exact/Brand/Comp
    {"Funnel Stage":"BOFU","Campaign Type":"Google Search","FORMAT":"Exact/Branded/Competitor",
     "TARGETING METHOD":"Exact brand + competitors; high-intent","WHAT DO WE NEED FOR TARGETING":"Exact lists; negatives; sitelinks",
     "CONTENT VISUAL SPECS":"—","CONTENT TEXTUAL SPECS":"Strong proof + urgency (pilot)","CONTENT VIDEO SPECS":"—",
     "AD DESTINATION":"Demo LP","Links to Visuals":"—","KPIs":"CVR, CPA, SQO rate"},
])

st.dataframe(content_df, use_container_width=True)
st.info("Narrative: **Create** demand with LI/YouTube, **Capture** with Google + LinkedIn retargeting, **Convert** with high-intent exact/branded search. Measure pre/post **behavior deltas** (adherence, incidents, time-to-competence).")

card_end()

# -----------------------------
# 4) QUICK WINS (Checklist)
# -----------------------------
card_start("4) Quick Wins to Capture Demand", "Immediate low-cost tactics to capture intent while scaling awareness")

st.markdown("""
✅ **Google Search — Exact & Competitor Terms**  
Capture high-intent queries around *serious games*, *behavior change training*, and competitor names (e.g., Gamelearn).  

✅ **LinkedIn Retargeting — Warm Audiences**  
Retarget website visitors, whitepaper readers, and video engagers with **Text/Conversation Ads** driving to a demo or pilot.  

✅ **Website Conversion Boost**  
Add CTAs like *“Book a Serious Game Demo”* or *“See Behavior Change in Action”*. Use sticky banners or exit intent popups.  

✅ **Repurpose EU Case Studies**  
Leverage Philips, ING, Bosch case studies in **US-facing landing pages and one-pagers** to build trust instantly.  

✅ **YouTube Retargeting (15s Demo Clip)**  
Low-CPM video retargeting for LinkedIn/Google engagers. Subtitled 15s clips = high recall, low cost.  

✅ **CRM List Uploads (if available)**  
Upload existing leads or EU lookalikes into LinkedIn/Google audiences for fast ABM activation.
""")

st.info("These moves ensure &ranj captures **real demand signals quickly** in the US while the broader strategy builds awareness and long-term pipeline.")

card_end()

