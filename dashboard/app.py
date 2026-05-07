import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Corporate Layoff Intelligence",
    page_icon="📉",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #f8fafc;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 95%;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.metric-card {
    background: linear-gradient(135deg, #111827, #1e293b);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #334155;
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    text-align: center;
    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-4px);
}

.metric-value {
    font-size: 32px;
    font-weight: 800;
    color: #f8fafc;
}

.metric-label {
    font-size: 14px;
    color: #94a3b8;
    margin-top: 8px;
}

.hero-card {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 25px;
    border: 1px solid #334155;
}

.section-title {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 20px;
    color: #f8fafc;
}

.insight-box {
    background: #111827;
    padding: 22px;
    border-radius: 16px;
    border-left: 5px solid #3b82f6;
    margin-top: 20px;
    margin-bottom: 20px;
    color: #e5e7eb;
    line-height: 1.7;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 18px;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #cbd5e1;
    font-weight: 600;
    padding: 10px 16px;
    border-radius: 10px;
}

.stTabs [aria-selected="true"] {
    background-color: #1e293b !important;
    color: white !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1f2937;
    border-radius: 12px;
    overflow: hidden;
}

.stDownloadButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
    font-weight: 600;
}

.stDownloadButton button:hover {
    background-color: #1d4ed8;
}

hr {
    border-color: #1f2937;
}

.small-text {
    color: #94a3b8;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/cleaned/layoffs_enriched.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df

df = load_data()

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="hero-card">
    <h1 style="margin:0;color:white;">📉 Corporate Layoff Intelligence Dashboard</h1>
    <p style="color:#cbd5e1;font-size:16px;margin-top:12px;">
    Analyze global workforce reduction patterns across industries, countries,
    funding stages, company maturity, and layoff severity.
    </p>
    <p style="color:#94a3b8;font-size:14px;">
    Workforce Analytics • Business Intelligence • Economic Trend Analysis
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("Dashboard Filters")

industries = sorted(df["industry"].dropna().unique())
countries = sorted(df["country"].dropna().unique())
stages = sorted(df["stage"].dropna().unique())

selected_industry = st.sidebar.multiselect(
    "Industry",
    industries,
    default=industries
)

selected_country = st.sidebar.multiselect(
    "Country",
    countries,
    default=countries
)

selected_stage = st.sidebar.multiselect(
    "Company Stage",
    stages,
    default=stages
)

min_year = int(df["year"].min())
max_year = int(df["year"].max())

selected_years = st.sidebar.slider(
    "Year Range",
    min_year,
    max_year,
    (min_year, max_year)
)

# Optional company search
search_company = st.sidebar.text_input("Search Company")

filtered_df = df[
    (df["industry"].isin(selected_industry)) &
    (df["country"].isin(selected_country)) &
    (df["stage"].isin(selected_stage)) &
    (df["year"].between(selected_years[0], selected_years[1]))
]

if search_company:
    filtered_df = filtered_df[
        filtered_df["company"].str.contains(search_company, case=False, na=False)
    ]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_laid_off = int(filtered_df["total_laid_off"].sum())
total_companies = filtered_df["company"].nunique()
total_countries = filtered_df["country"].nunique()
avg_percentage = round(filtered_df["percentage_laid_off"].mean() * 100, 2)

top_industry = (
    filtered_df.groupby("industry")["total_laid_off"]
    .sum()
    .idxmax()
)

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_laid_off:,}</div>
        <div class="metric-label">Employees Laid Off</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_companies:,}</div>
        <div class="metric-label">Affected Companies</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_countries}</div>
        <div class="metric-label">Countries Affected</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_percentage}%</div>
        <div class="metric-label">Average Workforce Reduction Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{top_industry}</div>
        <div class="metric-label">Most Affected Industry</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Overview",
    "Industry Analysis",
    "Geographic Impact",
    "Funding & Stage Risk",
    "Severity Intelligence"
])

# -----------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -----------------------------
with tab1:
    st.markdown('<div class="section-title">Executive Workforce Overview</div>', unsafe_allow_html=True)

    monthly_layoffs = (
        filtered_df.groupby("year_month")["total_laid_off"]
        .sum()
        .reset_index()
        .sort_values("year_month")
    )

    fig_time = px.line(
        monthly_layoffs,
        x="year_month",
        y="total_laid_off",
        markers=True,
        title="Monthly Layoff Trend",
        height=520
    )
    fig_time.update_layout(template="plotly_dark")

    st.plotly_chart(fig_time, use_container_width=True)

    colA, colB = st.columns([1, 1.3])

    with colA:
        st.markdown("""
        <div class="insight-box">
        <b>Business Insight</b><br><br>
        Layoff spikes may indicate economic pressure, sector-wide restructuring,
        or company-level cost-cutting cycles. Monthly trend analysis helps identify
        when workforce instability accelerated.
        </div>
        """, unsafe_allow_html=True)

    with colB:
        largest_events = (
            filtered_df.sort_values("total_laid_off", ascending=False)
            [["company", "industry", "country", "total_laid_off", "date"]]
            .head(10)
        )

        st.subheader("Largest Layoff Events")
        st.dataframe(largest_events, use_container_width=True)

    st.subheader("Key Executive Insights")

    insight1, insight2, insight3 = st.columns(3)

    with insight1:
        st.markdown("""
        <div class="insight-box">
        <b>Industry Risk</b><br><br>
        Workforce reductions are concentrated in specific industries,
        showing where restructuring pressure is strongest.
        </div>
        """, unsafe_allow_html=True)

    with insight2:
        st.markdown("""
        <div class="insight-box">
        <b>Funding Observation</b><br><br>
        Highly funded companies can still experience major layoffs,
        suggesting capital alone does not guarantee stability.
        </div>
        """, unsafe_allow_html=True)

    with insight3:
        st.markdown("""
        <div class="insight-box">
        <b>Economic Volatility</b><br><br>
        Layoff spikes often reflect broader uncertainty, changing demand,
        and business model corrections.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# TAB 2: INDUSTRY ANALYSIS
# -----------------------------
with tab2:
    st.markdown('<div class="section-title">Industry Risk Analysis</div>', unsafe_allow_html=True)

    industry_chart = (
        filtered_df.groupby("industry")
        .agg(
            total_laid_off=("total_laid_off", "sum"),
            affected_companies=("company", "nunique"),
            avg_percentage_laid_off=("percentage_laid_off", "mean")
        )
        .reset_index()
        .sort_values("total_laid_off", ascending=False)
    )

    fig_industry = px.bar(
        industry_chart.head(12),
        x="industry",
        y="total_laid_off",
        color="total_laid_off",
        text_auto=True,
        title="Top Industries by Total Layoffs",
        height=500
    )
    fig_industry.update_layout(template="plotly_dark")

    st.plotly_chart(fig_industry, use_container_width=True)

    colA, colB = st.columns(2)

    with colA:
        fig_companies = px.bar(
            industry_chart.sort_values("affected_companies", ascending=False).head(12),
            x="industry",
            y="affected_companies",
            color="affected_companies",
            text_auto=True,
            title="Industries by Number of Affected Companies",
            height=460
        )
        fig_companies.update_layout(template="plotly_dark")
        st.plotly_chart(fig_companies, use_container_width=True)

    with colB:
        fig_pct = px.bar(
            industry_chart.sort_values("avg_percentage_laid_off", ascending=False).head(12),
            x="industry",
            y="avg_percentage_laid_off",
            color="avg_percentage_laid_off",
            text_auto=".2f",
            title="Industries by Average Workforce Reduction %",
            height=460
        )
        fig_pct.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pct, use_container_width=True)

# -----------------------------
# TAB 3: GEOGRAPHIC IMPACT
# -----------------------------
with tab3:
    st.markdown('<div class="section-title">Geographic Layoff Impact</div>', unsafe_allow_html=True)

    country_chart = (
        filtered_df.groupby("country")["total_laid_off"]
        .sum()
        .reset_index()
        .sort_values("total_laid_off", ascending=False)
    )

    fig_country = px.bar(
        country_chart.head(15),
        x="country",
        y="total_laid_off",
        color="total_laid_off",
        text_auto=True,
        title="Top Countries by Total Layoffs",
        height=500
    )
    fig_country.update_layout(template="plotly_dark")

    st.plotly_chart(fig_country, use_container_width=True)

    # -----------------------------
    # GLOBAL LAYOFF HEATMAP
    # -----------------------------
    st.subheader("Global Layoff Heatmap")

    fig_map = px.choropleth(
        country_chart,
        locations="country",
        locationmode="country names",
        color="total_laid_off",
        hover_name="country",
        color_continuous_scale="Reds",
        title="Global Workforce Reduction Heatmap",
        height=650
    )

    fig_map.update_layout(template="plotly_dark")

    st.plotly_chart(fig_map, use_container_width=True)

    location_chart = (
        filtered_df.groupby("location")["total_laid_off"]
        .sum()
        .reset_index()
        .sort_values("total_laid_off", ascending=False)
        .head(15)
    )

    fig_location = px.bar(
        location_chart,
        x="location",
        y="total_laid_off",
        color="total_laid_off",
        text_auto=True,
        title="Top Locations by Layoffs",
        height=500
    )

    fig_location.update_layout(template="plotly_dark")

    st.plotly_chart(fig_location, use_container_width=True)

# -----------------------------
# TAB 4: FUNDING & STAGE RISK
# -----------------------------
with tab4:
    st.markdown('<div class="section-title">Funding and Company Stage Risk</div>', unsafe_allow_html=True)

    fig_scatter = px.scatter(
        filtered_df,
        x="funds_raised",
        y="total_laid_off",
        color="industry",
        size="total_laid_off",
        hover_data=["company", "stage", "country"],
        title="Funding Raised vs Employees Laid Off",
        height=600
    )
    fig_scatter.update_layout(template="plotly_dark")

    st.plotly_chart(fig_scatter, use_container_width=True)

    colA, colB = st.columns(2)

    with colA:
        stage_chart = (
            filtered_df.groupby("stage")["total_laid_off"]
            .sum()
            .reset_index()
            .sort_values("total_laid_off", ascending=False)
        )

        fig_stage = px.pie(
            stage_chart,
            names="stage",
            values="total_laid_off",
            title="Layoffs by Company Stage",
            hole=0.45,
            height=460
        )
        fig_stage.update_layout(template="plotly_dark")
        st.plotly_chart(fig_stage, use_container_width=True)

    with colB:
        stage_companies = (
            filtered_df.groupby("stage")["company"]
            .nunique()
            .reset_index()
            .sort_values("company", ascending=False)
        )

        fig_stage_bar = px.bar(
            stage_companies,
            x="stage",
            y="company",
            color="company",
            text_auto=True,
            title="Affected Companies by Stage",
            height=460
        )
        fig_stage_bar.update_layout(template="plotly_dark")
        st.plotly_chart(fig_stage_bar, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Interpretation Tip</b><br><br>
    If high-funded or post-IPO companies show large layoffs, this may suggest
    that funding alone does not guarantee workforce stability. This is one of
    the strongest business stories in the project.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# TAB 5: SEVERITY INTELLIGENCE
# -----------------------------
with tab5:
    st.markdown('<div class="section-title">Layoff Severity Intelligence</div>', unsafe_allow_html=True)

    severity_table = (
        filtered_df.sort_values("severity_score", ascending=False)
        [[
            "company",
            "industry",
            "country",
            "stage",
            "total_laid_off",
            "percentage_laid_off",
            "funds_raised",
            "severity_score"
        ]]
        .head(20)
    )

    st.subheader("Highest Severity Layoff Events")
    st.dataframe(severity_table, use_container_width=True, height=420)

    fig_severity = px.bar(
        severity_table.head(10),
        x="company",
        y="severity_score",
        color="severity_score",
        text_auto=".2f",
        title="Top 10 Companies by Layoff Severity Score",
        height=520
    )
    fig_severity.update_layout(template="plotly_dark")

    st.plotly_chart(fig_severity, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Why Severity Score Matters</b><br><br>
    Total layoffs alone can make large companies dominate the analysis.
    Severity score combines workforce reduction percentage and layoff size,
    helping identify companies where layoffs were especially severe relative to scale.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# DOWNLOAD SECTION
# -----------------------------
st.markdown("---")
st.subheader("Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_layoff_analysis.csv",
    mime="text/csv"
)

st.markdown("""
---
<div style='text-align:center; padding-top:10px;'>
<h4 style='color:#e5e7eb;'>Corporate Layoff Intelligence Platform</h4>
<p style='color:#94a3b8;'>Built with Python, Pandas, Plotly, and Streamlit</p>
<p style='color:#64748b; font-size:13px;'>
Workforce Analytics • Business Intelligence • Economic Trend Analysis
</p>
</div>
""", unsafe_allow_html=True)
