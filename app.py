"""Sustainable Energy for All — Interactive Dashboard.

5DATA004W Individual Coursework
Vihara Thejaka Kularathna (W2053281)
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import (
    load_se4all,
    get_countries_only,
    INDICATOR_LABELS,
)

# ---------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Sustainable Energy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------
PRIMARY = "#14B8A6"
PRIMARY_DARK = "#0F766E"
ACCENT_AMBER = "#F59E0B"
ACCENT_ROSE = "#EC4899"
ACCENT_EMERALD = "#10B981"
ACCENT_VIOLET = "#8B5CF6"
INK = "#0F172A"
MUTED = "#64748B"
BG_SOFT = "#F7F7FB"
BORDER = "#E2E8F0"

SEQUENTIAL_SCALE = "Tealgrn"
DIVERGING_SCALE = "RdYlGn"
QUALITATIVE_PALETTE = px.colors.qualitative.Safe

# Global CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 1px 3px rgba(15,23,42,0.04), 0 4px 12px rgba(15,23,42,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 6px rgba(15,23,42,0.06), 0 10px 20px rgba(15,23,42,0.05);
    }
    .kpi-icon {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        color: white;
    }
    .kpi-body { flex: 1; min-width: 0; }
    .kpi-label {
        font-size: 0.78rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 500;
        margin-bottom: 0.15rem;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
        margin-bottom: 0.15rem;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 500;
    }
    button[data-baseweb="tab"] {
        font-weight: 500 !important;
        padding: 0.6rem 1rem !important;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0F172A;
        margin: 0.5rem 0 0.6rem 0;
        letter-spacing: -0.01em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------
@st.cache_data
def get_data() -> pd.DataFrame:
    return load_se4all()

df = get_data()
countries_df = get_countries_only(df)

# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
st.sidebar.title("Controls")

year_min, year_max = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1,
)

indicator_options = list(INDICATOR_LABELS.keys())
indicator = st.sidebar.selectbox(
    "Primary indicator",
    options=indicator_options,
    format_func=lambda x: INDICATOR_LABELS[x],
    index=0,
)

default_countries = ["United Kingdom", "United States", "India", "China", "Germany", "Brazil"]
available_countries = sorted(countries_df["country"].unique())
selected_countries = st.sidebar.multiselect(
    "Countries to highlight",
    options=available_countries,
    default=[c for c in default_countries if c in available_countries],
)

show_aggregates = st.sidebar.checkbox(
    "Include regional aggregates (World, EU, etc.)",
    value=False,
    help="Includes entries like 'World', 'European Union', income groups.",
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data source: World Bank — Sustainable Energy for All (SE4ALL). "
    "[Open in DataBank](https://databank.worldbank.org/source/sustainable-energy-for-all)"
)

# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------
st.title("Sustainable Energy for All — Global Dashboard")
st.caption(
    "5DATA004W Individual Coursework — Vihara Thejaka Kularathna (W2053281) · "
    f"Showing data for {year_range[0]}–{year_range[1]} · "
    "Data: World Bank SE4ALL"
)

base_df = df if show_aggregates else countries_df
filtered = base_df[
    (base_df["year"] >= year_range[0]) & (base_df["year"] <= year_range[1])
].copy()

# ---------------------------------------------------------------------
# KPI card helper + icons
# ---------------------------------------------------------------------
ICON_GLOBE = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>'
ICON_TROPHY = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>'
ICON_TREND_DOWN = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>'
ICON_TREND_UP = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>'


def kpi_card(icon_svg: str, icon_bg: str, label: str, value: str, sub: str = "") -> str:
    sub_block = f'<div class="kpi-sub">{sub}</div>' if sub else '<div class="kpi-sub">&nbsp;</div>'
    html = (
        f'<div class="kpi-card">'
        f'<div class="kpi-icon" style="background: {icon_bg};">{icon_svg}</div>'
        f'<div class="kpi-body">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{sub_block}'
        f'</div>'
        f'</div>'
    )
    return html


# ---------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------
tab_overview, tab_map, tab_trends, tab_corr, tab_data = st.tabs([
    "Overview", "Map", "Trends", "Correlation", "Data",
])

# ----------------------------- OVERVIEW TAB -----------------------------
with tab_overview:
    st.markdown(
        f'<div class="section-title">Key metrics — {INDICATOR_LABELS[indicator]}</div>',
        unsafe_allow_html=True,
    )

    countries_filtered = countries_df[
        (countries_df["year"] >= year_range[0]) &
        (countries_df["year"] <= year_range[1])
    ].dropna(subset=[indicator])

    if len(countries_filtered) > 0:
        latest_year = int(countries_filtered["year"].max())
        latest_snapshot = countries_filtered[countries_filtered["year"] == latest_year]

        global_mean = latest_snapshot[indicator].mean()
        top_row = latest_snapshot.nlargest(1, indicator).iloc[0]
        bottom_row = latest_snapshot.nsmallest(1, indicator).iloc[0]

        first_year = int(countries_filtered["year"].min())
        start_snapshot = countries_filtered[countries_filtered["year"] == first_year][["country", indicator]]
        end_snapshot = latest_snapshot[["country", indicator]]
        change = end_snapshot.merge(start_snapshot, on="country", suffixes=("_end", "_start"))
        change["delta"] = change[f"{indicator}_end"] - change[f"{indicator}_start"]
        biggest_improver = change.nlargest(1, "delta").iloc[0] if len(change) else None

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                kpi_card(ICON_GLOBE, ACCENT_AMBER, f"Global average · {latest_year}", f"{global_mean:,.1f}"),
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                kpi_card(ICON_TROPHY, ACCENT_EMERALD, f"Highest · {latest_year}", f"{top_row[indicator]:,.1f}", top_row["country"]),
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                kpi_card(ICON_TREND_DOWN, ACCENT_ROSE, f"Lowest · {latest_year}", f"{bottom_row[indicator]:,.1f}", bottom_row["country"]),
                unsafe_allow_html=True,
            )
        with col4:
            if biggest_improver is not None:
                st.markdown(
                    kpi_card(ICON_TREND_UP, ACCENT_VIOLET, f"Largest change · {first_year}–{latest_year}", f"{biggest_improver['delta']:+,.1f}", biggest_improver["country"]),
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # Two-column preview charts
        ov_col1, ov_col2 = st.columns(2)

        with ov_col1:
            st.markdown(
                f'<div class="section-title">Geographic distribution · {latest_year}</div>',
                unsafe_allow_html=True,
            )
            ov_map = px.choropleth(
                latest_snapshot.dropna(subset=[indicator]),
                locations="country_code",
                color=indicator,
                hover_name="country",
                hover_data={"country_code": False, indicator: ":,.2f"},
                color_continuous_scale=SEQUENTIAL_SCALE,
                labels={indicator: INDICATOR_LABELS[indicator]},
            )
            ov_map.update_layout(
                height=320,
                margin=dict(l=0, r=0, t=10, b=0),
                geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
                coloraxis_colorbar=dict(thickness=10, len=0.7, title=None),
            )
            st.plotly_chart(ov_map, use_container_width=True)

        with ov_col2:
            st.markdown(
                f'<div class="section-title">Global trend · {first_year}–{latest_year}</div>',
                unsafe_allow_html=True,
            )
            global_trend = (
                countries_filtered.groupby("year")[indicator]
                .mean()
                .reset_index()
            )
            ov_line = px.area(
                global_trend,
                x="year", y=indicator,
                labels={"year": "Year", indicator: INDICATOR_LABELS[indicator]},
            )
            ov_line.update_traces(
                line=dict(color=PRIMARY, width=2.5),
                fillcolor="rgba(20, 184, 166, 0.15)",
            )
            ov_line.update_layout(
                height=320,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#E2E8F0", title=None),
                plot_bgcolor="white",
            )
            st.plotly_chart(ov_line, use_container_width=True)

        st.caption(
            f"Average across all countries: {global_mean:.1f} in {latest_year}. "
            f"For deeper analysis, see the Map, Trends, and Correlation tabs."
        )

    else:
        st.warning("No data available for this filter combination.")

# ----------------------------- MAP TAB -----------------------------
with tab_map:
    st.subheader(f"Global map — {INDICATOR_LABELS[indicator]}")

    map_year = st.slider(
        "Map year",
        min_value=year_range[0],
        max_value=year_range[1],
        value=year_range[1],
        step=1,
        key="map_year",
    )

    map_df = countries_df[
        countries_df["year"] == map_year
    ].dropna(subset=[indicator])

    if len(map_df) == 0:
        st.warning(f"No data available for {map_year}. Try a different year.")
    else:
        fig_map = px.choropleth(
            map_df,
            locations="country_code",
            color=indicator,
            hover_name="country",
            hover_data={"country_code": False, indicator: ":,.2f"},
            color_continuous_scale=SEQUENTIAL_SCALE,
            labels={indicator: INDICATOR_LABELS[indicator]},
            title=f"{INDICATOR_LABELS[indicator]} — {map_year}",
        )
        fig_map.update_layout(
            height=550,
            margin=dict(l=0, r=0, t=50, b=0),
            geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption(
            f"Showing {len(map_df)} countries with data for {map_year}. "
            "Hover over countries for exact values."
        )

# ----------------------------- TRENDS TAB -----------------------------
with tab_trends:
    st.subheader(f"Trends over time — {INDICATOR_LABELS[indicator]}")

    if not selected_countries:
        st.warning("Select one or more countries in the sidebar to see trends.")
    else:
        ts_df = countries_df[
            (countries_df["country"].isin(selected_countries)) &
            (countries_df["year"] >= year_range[0]) &
            (countries_df["year"] <= year_range[1])
        ].dropna(subset=[indicator])

        if len(ts_df) > 0:
            fig_ts = px.line(
                ts_df,
                x="year", y=indicator, color="country", markers=True,
                color_discrete_sequence=QUALITATIVE_PALETTE,
                labels={"year": "Year", indicator: INDICATOR_LABELS[indicator], "country": "Country"},
                title=f"{INDICATOR_LABELS[indicator]} · {year_range[0]}–{year_range[1]}",
            )
            fig_ts.update_layout(
                height=500,
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                margin=dict(l=0, r=0, t=50, b=0),
            )
            fig_ts.update_traces(line=dict(width=2.5))
            st.plotly_chart(fig_ts, use_container_width=True)

            ts_change = (
                ts_df.sort_values("year").groupby("country")[indicator]
                .agg(["first", "last"])
                .assign(delta=lambda d: d["last"] - d["first"])
                .sort_values("delta", ascending=False)
            )
            if len(ts_change) > 0:
                top_mover = ts_change.index[0]
                top_delta = ts_change["delta"].iloc[0]
                direction = "increased" if top_delta >= 0 else "decreased"
                st.caption(
                    f"Among selected countries, {top_mover} {direction} the most "
                    f"({top_delta:+.1f}) between {year_range[0]} and {year_range[1]}."
                )

    st.markdown("---")
    st.subheader(f"Country rankings — {INDICATOR_LABELS[indicator]}")

    rank_col1, rank_col2 = st.columns([1, 3])
    with rank_col1:
        rank_year = st.slider(
            "Ranking year",
            min_value=year_range[0], max_value=year_range[1],
            value=year_range[1], step=1, key="rank_year",
        )
        rank_mode = st.radio("Show", options=["Top 10", "Bottom 10", "Top & Bottom 5"], index=0)

    with rank_col2:
        rank_df = countries_df[countries_df["year"] == rank_year].dropna(subset=[indicator])
        if len(rank_df) > 0:
            if rank_mode == "Top 10":
                plot_df = rank_df.nlargest(10, indicator)
                colour_scale = SEQUENTIAL_SCALE
            elif rank_mode == "Bottom 10":
                plot_df = rank_df.nsmallest(10, indicator)
                colour_scale = [[0, "#FCA5A5"], [1, "#991B1B"]]
            else:
                top5 = rank_df.nlargest(5, indicator)
                bot5 = rank_df.nsmallest(5, indicator)
                plot_df = pd.concat([top5, bot5])
                colour_scale = DIVERGING_SCALE

            fig_bar = px.bar(
                plot_df.sort_values(indicator, ascending=True),
                x=indicator, y="country", orientation="h",
                color=indicator, color_continuous_scale=colour_scale,
                labels={indicator: INDICATOR_LABELS[indicator], "country": ""},
                title=f"{rank_mode} — {rank_year}", text=indicator,
            )
            fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig_bar.update_layout(height=450, margin=dict(l=0, r=0, t=50, b=0), coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------- CORRELATION TAB -----------------------------
with tab_corr:
    st.subheader("Indicator correlation")
    st.caption("Explore whether two indicators move together. Each point represents one country for the selected year.")

    scatter_col1, scatter_col2 = st.columns(2)
    with scatter_col1:
        x_indicator = st.selectbox(
            "X-axis indicator", options=indicator_options,
            format_func=lambda x: INDICATOR_LABELS[x], index=0, key="x_indicator",
        )
    with scatter_col2:
        y_indicator = st.selectbox(
            "Y-axis indicator", options=indicator_options,
            format_func=lambda x: INDICATOR_LABELS[x], index=3, key="y_indicator",
        )

    scatter_year = st.slider(
        "Year", min_value=year_range[0], max_value=year_range[1],
        value=year_range[1], step=1, key="scatter_year",
    )

    scatter_df = countries_df[
        countries_df["year"] == scatter_year
    ].dropna(subset=[x_indicator, y_indicator, "total_electricity_gwh"])

    if x_indicator == y_indicator:
        st.info("Select two different indicators on the X and Y axes to examine a relationship.")
    elif len(scatter_df) < 10:
        st.warning(f"Not enough data points for {scatter_year}.")
    else:
        fig_scatter = px.scatter(
            scatter_df,
            x=x_indicator, y=y_indicator, hover_name="country",
            size="total_electricity_gwh", size_max=40,
            color="renewable_energy_pct", color_continuous_scale=SEQUENTIAL_SCALE,
            labels={
                x_indicator: INDICATOR_LABELS[x_indicator],
                y_indicator: INDICATOR_LABELS[y_indicator],
                "renewable_energy_pct": "Renewable %",
                "total_electricity_gwh": "Total electricity (GWh)",
            },
            title=f"{INDICATOR_LABELS[y_indicator]} vs {INDICATOR_LABELS[x_indicator]} — {scatter_year}",
            trendline="ols",
        )
        fig_scatter.update_layout(height=550, margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig_scatter, use_container_width=True)

        correlation = scatter_df[x_indicator].corr(scatter_df[y_indicator])
        corr_strength = (
            "strong" if abs(correlation) > 0.7
            else "moderate" if abs(correlation) > 0.4
            else "weak"
        )
        corr_direction = "positive" if correlation > 0 else "negative"
        st.caption(
            f"Pearson correlation: {correlation:+.2f} — a {corr_strength} {corr_direction} relationship. "
            f"Bubble size represents total electricity output; colour represents renewable energy share."
        )

# ----------------------------- DATA TAB -----------------------------
with tab_data:
    st.subheader("Filtered data")
    st.write(f"{len(filtered):,} rows · {filtered['country'].nunique()} countries/regions")

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"se4all_filtered_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv",
    )

    st.dataframe(filtered, use_container_width=True)