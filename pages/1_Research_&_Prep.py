import os
import pandas as pd
import altair as alt

# Reuse helpers from app.py (cards & KPI chips)
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
st.set_page_config(page_title="Part X – <Page Name>", layout="wide")  # or "centered" where you want

from ui import card_start, card_end, kpi_chip, inject_google_css




st.title("Part 1 – Research & Prep (Behavior Change Focus)")


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# ---------- Utilities ----------
@st.cache_data
def load_csv(path: str, fallback_df: pd.DataFrame) -> pd.DataFrame:
    try:
        if os.path.exists(path):
            df = pd.read_csv(path)
            return df
        return fallback_df.copy()
    except Exception:
        return fallback_df.copy()

def df_exists(name: str) -> bool:
    return os.path.exists(os.path.join(DATA_DIR, name))

# ---------- Fallback (mock) data for non-market blocks ----------
channel_fallback = pd.DataFrame({
    "channel": ["LinkedIn","Google Search","YouTube","Bing Search"],
    "est_audience": [7000000, 150000, 210000000, 60000],
    "typical_role_fit": ["CHRO/L&D/Compliance/HSE","Director+Manager","All","Director+Manager"],
    "cpc_low": [4.0, 3.0, 0.02, 2.0],
    "cpc_high":[9.0, 8.0, 0.05, 6.0],
    "funnel_role": ["Create+Capture","Capture","Create","Capture"]
})

icp_fallback = pd.DataFrame({
    "industry": ["Healthcare","Manufacturing","Finance","Logistics","Retail","Government/Education"],
    "company_size_min":[1000,500,1000,500,500,1000],
    "company_size_max":[10000,5000,10000,5000,5000,20000],
    "region":["East Coast","Midwest","West Coast","Southwest","East Coast","Nationwide"],
    "primary_role":["Head of L&D","Compliance Director","CHRO","HSE Manager","Operations Director","Head of L&D"],
    "accounts":[320,210,180,140,160,260],
})

competitors_fallback = pd.DataFrame({
    "company":["Gamelearn","AllenComm","ELB Learning","Docebo","&ranj"],
    "focus":["Compliance/HR","Custom eLearning","Platforms+Content","LMS + Modules","Behavior Change Serious Games"],
    "strength":["US footprint; content library","LMS integrations; custom builds","Scale; tooling","Ecosystem; brand","UX; measurable behavior change; European enterprise proof"],
    "gap":["Customization depth","Gamification depth","Behavior-change proof","Custom simulations","US presence nascent; references to adapt"],
})

# Load CSVs for non-market blocks if present
channel_df = load_csv(os.path.join(DATA_DIR, "channel_reach.csv"), channel_fallback)
icp_df = load_csv(os.path.join(DATA_DIR, "icp_mock.csv"), icp_fallback)
competitors_df = load_csv(os.path.join(DATA_DIR, "competitors.csv"), competitors_fallback)

# =========================
# Real market data (from sources you shared)
# =========================
# Yahoo Finance – Global Corporate Training Market Report (value + CAGR)
GLOBAL_MARKET_USD_B = 352.66     # billions USD
GLOBAL_CAGR_PCT = 11.7           # % projected

# Rcademy – North America share
NA_SHARE_PCT = 46.0
ROW_SHARE_PCT = 100.0 - NA_SHARE_PCT

# LearnExperts – per-employee spend, budget growth
US_SPEND_PER_EMP = 1207          # USD per employee (approx)
US_SPEND_PER_EMP_LARGE = 722     # USD per employee (10k+ orgs)
AVG_BUDGET_PREV_M = 10.2         # million USD
AVG_BUDGET_CURR_M = 13.3         # million USD

# Derived dataframes for charts
market_size_kpis_df = pd.DataFrame({
    "Metric": ["Global Market (USD B)", "Expected CAGR (%)", "NA Share (%)"],
    "Value": [GLOBAL_MARKET_USD_B, GLOBAL_CAGR_PCT, NA_SHARE_PCT]
})

region_split_df = pd.DataFrame({
    "Region": ["North America", "Rest of World"],
    "SharePct": [NA_SHARE_PCT, ROW_SHARE_PCT]
})

per_employee_df = pd.DataFrame({
    "Category": ["US Average (behavioral enablement)", "Large Enterprise (10k+)"],
    "USD_per_employee": [US_SPEND_PER_EMP, US_SPEND_PER_EMP_LARGE]
})

budget_growth_df = pd.DataFrame({
    "Year": ["Last Year", "2024"],
    "Avg_Company_Training_Budget_MUSD": [AVG_BUDGET_PREV_M, AVG_BUDGET_CURR_M]
})

# ---------- Tabs ----------
tab_a, tab_b, tab_c, tab_d, tab_e = st.tabs([
    "Market Research",
    "Channel Reach",
    "ICP Explorer",
    "Competitors",
    "What We Need"
])


# =======================
# A) MARKET RESEARCH
# =======================
with tab_a:
    card_start("US & Global Market Snapshot (Behavior Outcomes Lens)", "Grounded in third-party data and tied to measurable behavior change")

    # KPI chips (behavior-oriented labeling)
    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi_chip("Global Market", f"${GLOBAL_MARKET_USD_B:,.2f}B")
    with k2: kpi_chip("CAGR (proj.)", f"{GLOBAL_CAGR_PCT:.1f}%", "green")
    with k3: kpi_chip("NA Share", f"{NA_SHARE_PCT:.0f}%", "yellow")
    with k4: kpi_chip("US Investment/Employee (to drive behavior)", f"${US_SPEND_PER_EMP:,}", "primary")

    st.divider()

    # ---- EXISTING chart: regional split
    col_top_left, col_top_right = st.columns([1.2, 1])
    with col_top_left:
        st.subheader("Regional Share (NA vs Rest)")
        st.altair_chart(
            alt.Chart(region_split_df).mark_arc(outerRadius=120).encode(
                theta="SharePct:Q",
                color=alt.Color("Region:N", legend=alt.Legend(title="Region")),
                tooltip=["Region","SharePct"]
            ).properties(height=320),
            use_container_width=True
        )

    # ---- Behavior-focused regional narrative
    st.subheader("Regional Highlights & Differences (Behavior Outcomes)")
    st.markdown("""
**Why this matters for &ranj (behavior-first):**
- **EU** → Demand driven by **ESG/compliance adherence**. Position serious games as **habit formation** that reduces audit findings and policy drift.
- **US/NA** → Higher per-employee investment requires **proof of behavior change**: **time-to-competence**, **first-time-right**, **error reduction**.
- **APAC** → Fast growth; emphasize **team-based adoption** and **behavioral rehearsal** (group workshops blended with simulations).
""")

    st.divider()

    # ---- Industries & behavior priorities
    st.subheader("Industries & Behavior Priorities (with Budget Signals)")
    industries_df = pd.DataFrame([
        {"Industry":"Banking/Financial Services","Behavior Priority":"Audit-ready adherence; policy application","Budget Signal":"~$1,097 per employee (training)"},
        {"Industry":"Healthcare","Behavior Priority":"Faster onboarding; procedure fidelity","Budget Signal":"High turnover (~18%) → onboarding focus"},
        {"Industry":"Manufacturing / HSE","Behavior Priority":"Safety behaviors; SOP adherence","Budget Signal":"OSHA programs; incident reduction"},
        {"Industry":"FMCG / Retail Ops","Behavior Priority":"Frontline consistency; CX behaviors","Budget Signal":"Large workforce; scale onboarding"},
        {"Industry":"IT / Tech","Behavior Priority":"Digital skill adoption; secure behaviors","Budget Signal":"Budgets rising; AI & digital skilling"},
    ])
    st.dataframe(industries_df, use_container_width=True)
    st.caption("Signals map to **behavior change outcomes** (fewer incidents, faster ramp, higher adherence). Replace/extend with client/analyst data when available.")

    st.divider()

    # ---- Investment per learner by size (kept chart, reframed)
    st.subheader("Behavioral Training Investment per Employee by Company Size (US)")
    per_learner_by_size = pd.DataFrame({
        "CompanySize": ["All Companies","Small (100–999)","Midsize (1,000–9,999)","Large (10,000+)"],
        "2022": [774, 1047, 739, 398],
        "2023": [954, 1396, 751, 481],
        "2024": [1207, 1420, 826, 722],
    })
    melted = per_learner_by_size.melt(id_vars="CompanySize", var_name="Year", value_name="USD_per_learner")
    perchart = alt.Chart(melted).mark_bar().encode(
        x=alt.X("CompanySize:N", title=None),
        y=alt.Y("USD_per_learner:Q", title="USD per employee (behavioral enablement)"),
        color=alt.Color("Year:N", legend=alt.Legend(title="Year")),
        tooltip=["CompanySize","Year","USD_per_learner"]
    ).properties(height=340)
    st.altair_chart(perchart, use_container_width=True)
    st.markdown("""
**Behavioral takeaway:** Smaller and midsize companies invest **more per employee** than very large enterprises — ideal for validating **behavior deltas** (pre/post) such as **time-to-competence** and **adherence**. Overall investment rose to **~$1,200** per employee in 2024.
""")

    st.markdown("""
- **Implication:** US budgets expect **outcome proof**. Propose KPIs like **first-time-right**, **policy adherence**, **incident rate deltas**.
- **Positioning:** Move the conversation from **knowledge** to **behavior**. Show how simulation scores transfer to field metrics.
- **Beachhead:** Mid-market to enterprise (1k–10k FTE) with **compliance, onboarding, and safety** where behaviors are observable.
    """)

    with st.expander("📚 Sources (click to expand)"):
        st.markdown("""
- Yahoo Finance — *Global Corporate Training Market Report*:  
  <https://uk.finance.yahoo.com/news/global-corporate-training-market-report-104300914.html>
- Rcademy — *Global Corporate Training Spend: Regional Trends and Forecasts for 2025*:  
  <https://rcademy.com/global-corporate-training-spend/>
- LearnExperts — *How Much Do Companies Spend on Training Per Employee?*:  
  <https://learnexperts.ai/blog/how-much-do-companies-spend-on-training-per-employee/>
        """, unsafe_allow_html=True)

    card_end()


# =======================
# B) CHANNEL REACH
# =======================
with tab_b:
    card_start("Channel Reach & Role (to Drive Behavior Change)", "Audience potential, CPC ranges, and how each channel contributes to behavior outcomes")
    st.caption("Note: Reach/CPCs are indicative; replace with platform-estimated numbers for final client deck.")

    # --- Deep-dive tabs for LinkedIn, Google Search & YouTube ---
    sub_li, sub_g, sub_y = st.tabs([
        "LinkedIn (Your Audience Estimate)",
        "Google Search (Keyword Planner)",
        "YouTube (Video Reach)"
    ])

    # --------------------------------
    # LINKEDIN (from your screenshots)
    # --------------------------------
    with sub_li:
        st.caption("Source: Your LinkedIn Campaign Manager estimates (United States).")

        li_total_us = 270_000_000        # All US members
        li_icp_est  = 100_000_000        # Your filtered ICP (job titles, skills, seniority, company size)

        li_function_share = pd.DataFrame([
            {"Function": "Business Development", "SharePct": 18},
            {"Function": "Operations",           "SharePct": 18},
            {"Function": "Sales",                "SharePct": 9},
            {"Function": "Healthcare Services",  "SharePct": 8},
            {"Function": "Education",            "SharePct": 7},
        ])
        li_function_share["Est_Audience"] = (li_function_share["SharePct"]/100.0) * li_icp_est

        st.subheader("LinkedIn ICP Breakdown by Function")
        st.altair_chart(
            alt.Chart(li_function_share).mark_bar().encode(
                x=alt.X("Function:N", title=None),
                y=alt.Y("Est_Audience:Q", title="Estimated Audience"),
                tooltip=["Function","SharePct","Est_Audience"]
            ).properties(height=330),
            use_container_width=True
        )

        st.dataframe(li_function_share, use_container_width=True)

        k1, k2, k3 = st.columns(3)
        with k1: kpi_chip("US LinkedIn Members", f"{li_total_us:,}")
        with k2: kpi_chip("Filtered ICP", f"{li_icp_est:,}", "primary")
        with k3: kpi_chip("Top Functions Coverage", f"≈{li_function_share['SharePct'].sum()}%", "yellow")

        st.markdown("""
**Behavioral messaging on LinkedIn:**
- Speak to **policy adoption**, **safety behaviors**, **reduced errors**, **faster ramp**.
- Optimize for **qualified forms** that request a **behavioral pilot (2-week sprint)**.
""")
        st.success("Use LinkedIn to influence the **buying committee** and build retargeting pools for **BOFU demos** focused on behavior impact.")

    # --------------------------------
    # GOOGLE SEARCH (Keyword Planner)
    # --------------------------------
    with sub_g:
        st.caption("Source: Google Ads Keyword Planner (US targeting). Currency in GBP as exported.")

        google_clusters = pd.DataFrame([
            {
                "Cluster": "Gamification / Learning",
                "Keywords (examples)": "gamification in education; gamified learning; gamification of learning; gamified education; gamification and learning",
                "Avg_Monthly_Searches": 6400,
                "CPC_Low_GBP": 1.42,
                "CPC_High_GBP": 11.70
            },
            {
                "Cluster": "Serious Games & Simulation",
                "Keywords (examples)": "serious gaming; management simulation games; business simulation training; business strategy games",
                "Avg_Monthly_Searches": 1610,
                "CPC_Low_GBP": 1.08,
                "CPC_High_GBP": 12.96
            },
        ])

        st.subheader("Google Search Keyword Clusters")
        st.altair_chart(
            alt.Chart(google_clusters).mark_bar().encode(
                x=alt.X("Cluster:N", title=None),
                y=alt.Y("Avg_Monthly_Searches:Q", title="Avg Monthly Searches"),
                tooltip=list(google_clusters.columns)
            ).properties(height=330),
            use_container_width=True
        )

        st.dataframe(google_clusters, use_container_width=True)
        st.write("**Use case:** Capture **high-intent** queries and route to **behavioral proof assets** (case studies showing incident reduction, time-to-competence, first-time-right).")

    # -------------------------------
    # YOUTUBE (benchmarked reach)
    # -------------------------------
    with sub_y:
        st.caption("Benchmarks for US. Narrowed ICP = HR/L&D/Compliance/Ops interests & in-market segments.")

        yt_df = pd.DataFrame([
            {"Segment": "US YouTube audience (base)", "Reach_est": 240_000_000},
            {"Segment": "Narrowed ICP (professionals)", "Reach_est": 8_000_000},
            {"Segment": "Retargeting pool", "Reach_est": 50_000},
        ])

        st.subheader("YouTube Estimated Reach")
        st.altair_chart(
            alt.Chart(yt_df).mark_bar().encode(
                x=alt.X("Segment:N", title=None),
                y=alt.Y("Reach_est:Q", title="Estimated Reach"),
                tooltip=["Segment","Reach_est"]
            ).properties(height=330),
            use_container_width=True
        )

        st.dataframe(yt_df, use_container_width=True)

        kpi_chip("ICP Reach (YouTube)", "8–15M", "primary")
        kpi_chip("Benchmark CPM", "$10–15", "green")
        st.write("**Best use:** TOFU awareness that **shows behavior in action** (decision branches, consequences), paired with **remarketing** to BOFU demo offers.")

    card_end()


# =======================
# C) ICP EXPLORER
# =======================
with tab_c:
    card_start("ICP Explorer", "Explore ideal customer profiles by tier, role, and region (behavior-first)")

    # --- Tiered ICP view ---
    st.subheader("ICP Tiers (Behavior Use Cases)")
    icp_df = pd.DataFrame([
        {"Tier": "A", "Industry": "Banking/Financial Services", "Company Size": "1,000–9,999", "Region": "US Northeast", "Key Roles": "CHRO, Compliance Director", "Behavioral Use Case": "Policy adherence, audit-ready behaviors"},
        {"Tier": "A", "Industry": "Healthcare", "Company Size": "1,000–9,999", "Region": "Midwest", "Key Roles": "CHRO, L&D Director", "Behavioral Use Case": "Faster onboarding; procedure fidelity"},
        {"Tier": "A", "Industry": "Manufacturing / HSE", "Company Size": "1,000–9,999", "Region": "Midwest", "Key Roles": "HSE, Ops VP", "Behavioral Use Case": "Safety incident reduction; SOP adherence"},
        {"Tier": "A", "Industry": "Tech / IT", "Company Size": "1,000–9,999", "Region": "West Coast", "Key Roles": "L&D, CHRO", "Behavioral Use Case": "Digital skill adoption; secure behaviors"},
        {"Tier": "B", "Industry": "FMCG / Retail", "Company Size": "500–999 or 10,000+", "Region": "National", "Key Roles": "HR, Ops, Sales Enablement", "Behavioral Use Case": "Frontline consistency; CX behaviors"},
        {"Tier": "B", "Industry": "Education / Public Sector", "Company Size": "500–999 or 10,000+", "Region": "National", "Key Roles": "HR, Compliance", "Behavioral Use Case": "Culture/DEI adoption; policy reinforcement"},
    ])
    st.dataframe(icp_df, use_container_width=True)

    st.divider()

    with st.expander("ℹ️ Why segment US by regions? (Click to expand)"):
        st.markdown("""
        **Reasoning for segmentation:**
        - **Northeast (Finance / HQ concentration):** New York, Boston → compliance-heavy behaviors (banking, insurance, corporates).  
        - **West Coast (Tech & Innovation):** Silicon Valley, Seattle → adoption of digital behaviors & secure practices.  
        - **Midwest (Healthcare & Manufacturing):** Chicago, Detroit, Minneapolis → safety and onboarding behaviors are observable.  
        - *(Optional expansion)* **South (FMCG, Energy, Logistics):** Dallas, Atlanta, Houston → frontline consistency & SOP adherence.
        """)

    st.info("**Behavior-first plan:** Start with Tier A industries (1k–10k FTE) where **behaviors are observable**. Run a 2-week pilot → measure **pre/post behavior deltas** → scale where lift is proven.")

    # --- Buying committee (behavior KPIs)
    st.subheader("Buying Committee & Personas (Behavior KPIs)")
    persona_df = pd.DataFrame([
        {"Role": "CHRO", "Decision Power": "Final approval", "Behavior KPI": "Retention lift; engagement index ↑", "Proof Needed": "Pre/post behavior metrics; ties to performance"},
        {"Role": "L&D Director", "Decision Power": "Key influencer", "Behavior KPI": "Time-to-competence ↓; application ↑", "Proof Needed": "Simulation→field transfer checks"},
        {"Role": "Compliance Officer", "Decision Power": "Veto power", "Behavior KPI": "Adherence ↑; audit findings ↓", "Proof Needed": "Completion→adherence linkage"},
        {"Role": "HSE Director", "Decision Power": "Influencer", "Behavior KPI": "Recordables ↓; near-misses ↓", "Proof Needed": "Scenario scores vs incident trend"},
        {"Role": "Ops / BU VP", "Decision Power": "Sponsor", "Behavior KPI": "First-time-right ↑; SOP deviations ↓", "Proof Needed": "Before/after productivity & quality"},
    ])
    st.dataframe(persona_df, use_container_width=True)

    # --- Interactive filter widget ---
    st.subheader("🎯 Explore ICP by Industry & Role")
    selected_industry = st.selectbox("Select Industry", sorted(icp_df["Industry"].unique()))
    selected_role = st.selectbox("Select Role", sorted(persona_df["Role"].unique()))

    # Filter logic
    ind_row = icp_df[icp_df["Industry"] == selected_industry].iloc[0]
    role_row = persona_df[persona_df["Role"] == selected_role].iloc[0]

    # Display cards
    st.markdown("### Selected Industry")
    st.markdown(f"""
    <div class="g-card">
    <h4>{ind_row['Industry']}</h4>
    <ul>
      <li><b>Tier:</b> {ind_row['Tier']}</li>
      <li><b>Company Size:</b> {ind_row['Company Size']}</li>
      <li><b>Region:</b> {ind_row['Region']}</li>
      <li><b>Key Roles:</b> {ind_row['Key Roles']}</li>
      <li><b>Behavioral Use Case:</b> {ind_row['Behavioral Use Case']}</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Selected Role")
    st.markdown(f"""
    <div class="g-card">
    <h4>{role_row['Role']}</h4>
    <ul>
      <li><b>Decision Power:</b> {role_row['Decision Power']}</li>
      <li><b>Behavior KPI:</b> {role_row['Behavior KPI']}</li>
      <li><b>Proof Needed:</b> {role_row['Proof Needed']}</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- Regional context (kept)
    st.subheader("Regional Priorities")
    st.markdown("""
    - **US:** ROI-driven, higher investment per employee; preference for digital/self-paced behavior rehearsal.
    - **EU:** Compliance & ESG-driven behaviors; strong audit orientation.
    - **APAC:** Fast growth; group-based learning behaviors; workshop + simulation blends.
    """)

    st.info("**Insight:** Measure what matters: **adherence, incidents, time-to-competence, first-time-right**. Scale programs where behavior lift is proven.")

    card_end()


# =======================
# D) COMPETITORS
# =======================
with tab_d:
    card_start("Competitors Landscape", "Direct & indirect competitors in the US (behavior impact vs content delivery)")

    st.subheader("Competitive Positioning Matrix")
    competitors_df = pd.DataFrame([
        {"Company": "&ranj", "Type": "Serious Games", "Engagement": 9, "Presence": 6},
        {"Company": "Skillsoft", "Type": "LMS / e-learning", "Engagement": 4, "Presence": 9},
        {"Company": "AllenComm", "Type": "Custom Training", "Engagement": 6, "Presence": 6},
        {"Company": "SweetRush", "Type": "Gamification Agency", "Engagement": 7, "Presence": 5},
        {"Company": "Gamelearn", "Type": "Serious Games", "Engagement": 8, "Presence": 5},
        {"Company": "Docebo", "Type": "Enterprise LMS", "Engagement": 5, "Presence": 8},
    ])

    chart = alt.Chart(competitors_df).mark_circle(size=300).encode(
        x=alt.X("Engagement:Q", scale=alt.Scale(domain=[0,10])),
        y=alt.Y("Presence:Q", scale=alt.Scale(domain=[0,10])),
        color=alt.Color("Type:N", legend=alt.Legend(title="Type")),
        tooltip=["Company","Type","Engagement","Presence"]
    ).properties(height=400)

    st.altair_chart(chart, use_container_width=True)

    st.subheader("Competitor Overview Table")
    st.dataframe(competitors_df, use_container_width=True)

    with st.expander("ℹ️ Scoring Methodology (Click to expand)"):
        st.markdown("""
        Scores are **directional (0–10)** to illustrate relative positioning:

        - **Engagement (X-axis):** Depth of **behavior rehearsal** (interactivity, simulations, decision-making).
          - 9 = immersive serious games
          - 4–5 = traditional content-centric e-learning
          - 6–7 = custom gamification or agency builds

        - **Presence (Y-axis):** US market footprint, brand recognition, scale of deployments.
          - 9 = global LMS giants (Skillsoft, Docebo)
          - 5–6 = mid-size agencies (AllenComm, SweetRush)
          - 6 = &ranj (strong EU proof; expanding US)

        **Goal:** Highlight &ranj’s **High Engagement / Growing Presence** vs LMS giants’ **High Presence / Low behavior rehearsal**.
        """)

    st.markdown("""
    **Behavioral Positioning Takeaways:**
    - **&ranj** → Highest **engagement-to-behavior** conversion (decision-making, consequences, spaced practice).  
    - **LMS giants (Skillsoft, Docebo)** → Strong presence, but **content-centric**; weaker at **behavior rehearsal**.  
    - **Custom agencies (AllenComm, SweetRush)** → Good gamification, slower to pilot; &ranj wins with **faster behavioral prototypes**.  
    - **Niche games (Gamelearn)** → Overlap on simulations; &ranj differentiates with **behavior metrics** and **EU enterprise proof**.
    """)

    # =======================
# E) WHAT WE NEED
# =======================
with tab_e:
    card_start("What We Need Before Launching Paid Strategy", "Checklist to ensure data, targeting, and creative foundations are in place")

    st.markdown("""
    Before activating campaigns, we need the following in place to ensure effectiveness, tracking accuracy, and alignment with &ranj’s **desired behavior change focus**:
    """)

    st.markdown("""
    1. **Access to ad platforms** – Google Ads, LinkedIn Campaign Manager, YouTube Ads  
    2. **Analytics & tracking setup** – GA4, Google Tag Manager, validated event tracking  
    3. **CRM integration** – HubSpot, Salesforce, or equivalent for lead nurturing & SQL handoff  
    4. **Define buying cycle & LTV** – understand decision timelines and customer value  
    5. **Conversion tracking** – clear events (form fills, demo requests, video views, downloads)  
    6. **UTM taxonomy** – consistent campaign tracking across all platforms  
    7. **Customer lists** – upload hashed first-party data into LinkedIn and Google Ads  
    8. **Landing pages** – dedicated, behavior-focused pages with clear CTAs and proof points  
    9. **UX analyzers** – Microsoft Clarity or Hotjar for behavior & engagement insights  
    10. **Content preparation** – whitepapers, thought-leadership pieces, and demo offers for MOFU/BOFU  
    11. **Creative readiness** – text ads, visuals, video, carousels segmented by funnel stage  
    12. **Testing plan** – A/B experiments for ads and landing pages  
    13. **Measurement framework** – CPM, CTR, CPC, CPA, CVR benchmarks agreed in advance  
    14. **Reporting cadence** – weekly pulse reports, monthly performance deep dives  
    """)

    st.info("✅ Once this foundation is in place, campaigns can launch with reduced risk of wasted spend, ensuring early learnings are reliable and scalable.")

    card_end()
