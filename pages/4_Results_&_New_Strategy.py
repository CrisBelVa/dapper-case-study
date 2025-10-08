# pages/4_Performance_Review.py
import streamlit as st
import pandas as pd
import altair as alt
from math import floor

from app import card_start, card_end, kpi_chip, inject_google_css

# after st.set_page_config(...)
inject_google_css()


st.set_page_config(page_title="Part 4 – Performance Review", layout="wide")
st.title("Part 4 – Performance Review (Simulated)")

# -----------------------------
# Scenario selector
# -----------------------------
st.caption(
    "Simulated results based on the proposed plan. "
    "Assumes LinkedIn/YouTube underperform on clicks (−40%) and global CVR = 1.0%."
)
scenario = st.radio("Select budget scenario", ["€15K / month", "€30K / month"], horizontal=True, index=0)

# Proposed monthly budgets per channel (aligned with Part 2 corrections)
base_budgets = {
    "LinkedIn – Awareness": 6000,
    "YouTube – Awareness": 2000,
    "Google Search – Generic (MOFU)": 3000,
    "Google Search – RLSA (MOFU)": 1000,
    "LinkedIn – Retargeting (MOFU)": 2000,
    "Google Search – Exact/Brand/Comp (BOFU)": 1000,
}
scale = 2 if "€30K" in scenario else 1
budgets = {k: v * scale for k, v in base_budgets.items()}

# -----------------------------
# Benchmarks & simulation rules
# -----------------------------
# Base CPC/CPM midpoints (euros)
benchmarks = {
    "LinkedIn – Awareness": {"cpc": 8.0, "cpm": 55.0},
    "YouTube – Awareness": {"cpc": 3.5, "cpm": 13.0},
    "Google Search – Generic (MOFU)": {"cpc": 5.8, "cpm": None},
    "Google Search – RLSA (MOFU)": {"cpc": 4.8, "cpm": None},
    "LinkedIn – Retargeting (MOFU)": {"cpc": 6.2, "cpm": 42.0},
    "Google Search – Exact/Brand/Comp (BOFU)": {"cpc": 4.5, "cpm": None},
}

# Underperformance: only LinkedIn & YouTube (−40% clicks → higher effective CPC; +20% CPM)
UNDERPERFORM_CLICK_CHANNELS = {
    "LinkedIn – Awareness",
    "LinkedIn – Retargeting (MOFU)",
    "YouTube – Awareness",
}
CLICK_REDUCTION_FACTOR = 0.60            # 40% fewer clicks than naive expectation
CPC_INFLATE_FOR_UNDERPERF = 1 / 0.60     # ≈ 1.6667, keeps Spend ≈ Clicks × CPC
CPM_INFLATE_FOR_UNDERPERF = 1.20         # +20% CPM on LI/YT

GLOBAL_CVR = 0.01   # 1% global conversion rate

# -----------------------------
# Build simulated performance
# -----------------------------
rows = []
for ch, spend in budgets.items():
    base_cpc = benchmarks[ch]["cpc"]
    base_cpm = benchmarks[ch]["cpm"]

    # Apply underperformance adjustments to LI & YT (not to Google Search)
    if ch in UNDERPERFORM_CLICK_CHANNELS:
        eff_cpc = base_cpc * CPC_INFLATE_FOR_UNDERPERF if base_cpc else None
        eff_cpm = base_cpm * CPM_INFLATE_FOR_UNDERPERF if base_cpm else None
    else:
        eff_cpc = base_cpc
        eff_cpm = base_cpm

    # Compute clicks from spend and effective CPC (Spend ≈ Clicks × CPC)
    clicks = (spend / eff_cpc) if eff_cpc else 0

    # Impressions:
    if eff_cpm:  # LI/YT (CPM known)
        impressions = spend / (eff_cpm / 1000.0)
        ctr = (clicks / impressions) if impressions > 0 else 0.0
    else:
        # Search: derive impressions from assumed CTR (keep stable for intent)
        assumed_ctr = 0.035 if "Generic" in ch else 0.055  # ~3.5% generic, ~5.5% exact/brand/comp
        impressions = clicks / assumed_ctr if assumed_ctr > 0 else 0
        ctr = assumed_ctr

    rows.append({
        "Channel": ch,
        "Spend (€)": round(spend, 2),
        "CPC (€)": round(eff_cpc, 2) if eff_cpc else "—",
        "CPM (€)": round(eff_cpm, 2) if eff_cpm else "—",
        "Impressions": int(impressions),
        "Clicks": int(clicks),
        "CTR": ctr,  # decimal
    })

df = pd.DataFrame(rows)

# Force global CVR across the whole mix (distribute by click share)
total_clicks = max(df["Clicks"].sum(), 1)
total_conversions = max(int(round(total_clicks * GLOBAL_CVR)), 1)
df["Click Share"] = df["Clicks"] / total_clicks
df["Conversions"] = (df["Click Share"] * total_conversions).round().astype(int)

# Ensure at least 1 conversion in highest-intent Search Exact/Brand/Comp
if df.loc[df["Channel"].str.contains("Exact/Brand/Comp"), "Conversions"].sum() == 0:
    idx = df.index[df["Channel"].str.contains("Exact/Brand/Comp")][0]
    df.at[idx, "Conversions"] = 1
    # Rebalance if rounding drift
    drift = total_conversions - df["Conversions"].sum()
    if drift != 0:
        idx_top = df["Clicks"].idxmax()
        df.at[idx_top, "Conversions"] = max(df.at[idx_top, "Conversions"] + drift, 0)

# CPA & SQLs (SQLs ≈ 30% of conversions)
df["CPA (€)"] = df.apply(lambda r: (r["Spend (€)"] / r["Conversions"]) if r["Conversions"] > 0 else None, axis=1)
df["SQLs"] = (df["Conversions"] * 0.30).round().astype(int)

# -----------------------------
# KPI chips
# -----------------------------
k1, k2, k3, k4 = st.columns(4)
with k1: kpi_chip("Spend (month)", f"€{int(df['Spend (€)'].sum()):,}")
with k2: kpi_chip("Impressions", f"{int(df['Impressions'].sum()):,}")
with k3: kpi_chip("Clicks", f"{int(df['Clicks'].sum()):,}")
with k4: kpi_chip("Global CVR", f"{GLOBAL_CVR*100:.1f}%", "yellow")

# =======================
# 1) Simulated Performance Stats
# =======================
card_start("1) Simulated Performance (Weeks 1–4)", "LI/YT click underperformance (−40%); CPM inflated; CVR fixed at 1%")
display_cols = ["Channel","Spend (€)","CPC (€)","CPM (€)","Impressions","Clicks","CTR","Conversions","CPA (€)","SQLs"]
df_display = df.copy()
df_display["CTR"] = (df_display["CTR"] * 100).round(2).astype(str) + "%"
df_display["CPA (€)"] = df_display["CPA (€)"].apply(lambda x: f"€{x:,.0f}" if pd.notnull(x) else "—")
st.dataframe(df_display[display_cols], use_container_width=True)

# Quick visuals
c1, c2 = st.columns(2)
with c1:
    st.subheader("Impressions by Channel")
    st.altair_chart(
        alt.Chart(df).mark_bar().encode(
            x=alt.X("Channel:N", title=None),
            y=alt.Y("Impressions:Q"),
            tooltip=["Channel","Impressions"]
        ).properties(height=320),
        use_container_width=True
    )
with c2:
    st.subheader("Clicks by Channel")
    st.altair_chart(
        alt.Chart(df).mark_bar().encode(
            x=alt.X("Channel:N", title=None),
            y=alt.Y("Clicks:Q"),
            tooltip=["Channel","Clicks"]
        ).properties(height=320),
        use_container_width=True
    )

# =======================
# 2) Insight Card (Positives) + Optimization Card
# =======================
st.divider()
c_left, c_right = st.columns([1.1, 1])
with c_left:
    card_start("What’s Working (Positives)", "Awareness & engagement signals")
    # Simulated site behavior improvements (these are narrative metrics for the story)
    engagement_uplift_pct = 18  # +18% vs. pre-campaign
    churn_drop_pct = 12         # -12% bounce/churn vs. pre-campaign
    st.markdown(f"""
- **Reach delivered as expected:** **{int(df['Impressions'].sum()):,}** impressions; strong video exposure via YouTube & LinkedIn.  
- **Audience fit:** early **SQLs = {df['SQLs'].sum()}** from Search & LI retargeting → ICP resonance (HR, L&D, Compliance).  
- **Site quality improving:** **engagement rate +{engagement_uplift_pct}%**, and **churn/bounce −{churn_drop_pct}%** since campaigns went live.  
- **Message recall:** view-through metrics and profile engagement trending positively for a cold US market.  
    """)
    card_end()

with c_right:
    card_start("Active Optimizations (In-flight)", "What the team is adjusting this week")
    st.markdown("""
- **Ad testing:** rotate pain-first angles (audit errors ↓ / incidents ↓ / ramp faster) vs. generic training claims.  
- **LP fixes:** shorten forms, move **“Book a 2-week pilot”** above the fold, keep **business email required**.  
- **Exclusions:** update negative KWs; enforce “people in location”; refine retargeting windows.  
- **Creative refresh:** pause <0.4% CTR LI assets after 5k impressions; replace within 48h.
    """)
    st.markdown("""
**Expected impact (2–4 weeks):**  
- **CPC ↓ 15–20%** • **CPA ↓ 25–30%** • **SQLs ↑ ~2×** • **Demo LP visits ↑**
    """)
    card_end()

# =======================
# 3) Budget Shift to Highest Intent (MOFU & BOFU)
# =======================
st.divider()
card_start("3) Budget Shift to Highest Intent (MOFU & BOFU)", "Reallocate for efficiency while keeping awareness on")

# Before (current)
before_df = pd.DataFrame([
    {"Funnel":"TOFU","Channel Group":"LinkedIn Awareness","Budget (€)": budgets["LinkedIn – Awareness"]},
    {"Funnel":"TOFU","Channel Group":"YouTube Awareness","Budget (€)": budgets["YouTube – Awareness"]},
    {"Funnel":"MOFU","Channel Group":"Google Search – Generic","Budget (€)": budgets["Google Search – Generic (MOFU)"]},
    {"Funnel":"MOFU","Channel Group":"Google Search – RLSA","Budget (€)": budgets["Google Search – RLSA (MOFU)"]},
    {"Funnel":"MOFU","Channel Group":"LinkedIn Retargeting","Budget (€)": budgets["LinkedIn – Retargeting (MOFU)"]},
    {"Funnel":"BOFU","Channel Group":"Google Search – Exact/Brand/Comp","Budget (€)": budgets["Google Search – Exact/Brand/Comp (BOFU)"]},
])

# After (proposed shift): pull 20% from TOFU and split to MOFU/BOFU (70/30)
pull = 0.20
li_shift = budgets["LinkedIn – Awareness"] * pull
yt_shift = budgets["YouTube – Awareness"] * pull
after_budgets = budgets.copy()
after_budgets["LinkedIn – Awareness"] -= li_shift
after_budgets["YouTube – Awareness"] -= yt_shift
add_mofu = (li_shift + yt_shift) * 0.70
add_bofu = (li_shift + yt_shift) * 0.30
# distribute to MOFU (Search Generic + LI Retargeting) & BOFU (Exact/Brand/Comp)
after_budgets["Google Search – Generic (MOFU)"] += add_mofu * 0.6
after_budgets["LinkedIn – Retargeting (MOFU)"] += add_mofu * 0.4
after_budgets["Google Search – Exact/Brand/Comp (BOFU)"] += add_bofu

after_df = pd.DataFrame([
    {"Funnel":"TOFU","Channel Group":"LinkedIn Awareness","Budget (€)": after_budgets["LinkedIn – Awareness"]},
    {"Funnel":"TOFU","Channel Group":"YouTube Awareness","Budget (€)": after_budgets["YouTube – Awareness"]},
    {"Funnel":"MOFU","Channel Group":"Google Search – Generic","Budget (€)": after_budgets["Google Search – Generic (MOFU)"]},
    {"Funnel":"MOFU","Channel Group":"Google Search – RLSA","Budget (€)": after_budgets["Google Search – RLSA (MOFU)"]},
    {"Funnel":"MOFU","Channel Group":"LinkedIn Retargeting","Budget (€)": after_budgets["LinkedIn – Retargeting (MOFU)"]},
    {"Funnel":"BOFU","Channel Group":"Google Search – Exact/Brand/Comp","Budget (€)": after_budgets["Google Search – Exact/Brand/Comp (BOFU)"]},
])

st.markdown("**Before → After (20% reallocation from TOFU to MOFU/BOFU)**")
bb1, bb2 = st.columns(2)
with bb1:
    st.write("**Before**")
    st.dataframe(before_df, use_container_width=True)
with bb2:
    st.write("**After**")
    st.dataframe(after_df, use_container_width=True)

st.altair_chart(
    alt.Chart(pd.concat([before_df.assign(View="Before"), after_df.assign(View="After")]))
      .mark_bar()
      .encode(
          x=alt.X("Channel Group:N", title=None),
          y=alt.Y("Budget (€):Q"),
          color=alt.Color("View:N"),
          column=alt.Column("Funnel:N")
      ).properties(height=300),
    use_container_width=True
)

st.info(
    "We’ll keep awareness **on**, but reallocate ~20% to **MOFU/BOFU** (Search + LI Retargeting) "
    "to reduce **CPC/CPA** and increase **SQLs** over the next 2–4 weeks."
)

card_end()
