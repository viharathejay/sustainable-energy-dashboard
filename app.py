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
# Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Sustainable Energy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# Load data (cached so it doesn't reload on every interaction)
# ---------------------------------------------------------------------
@st.cache_data
def get_data() -> pd.DataFrame:
    return load_se4all()

df = get_data()
countries_df = get_countries_only(df)

# ---------------------------------------------------------------------
# Sidebar — filters
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

# Filtered dataset (used across tabs)
base_df = df if show_aggregates else countries_df
filtered = base_df[
    (base_df["year"] >= year_range[0]) & (base_df["year"] <= year_range[1])
].copy()

# ---------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------
tab_overview, tab_map, tab_trends, tab_corr, tab_data = st.tabs([
    "Overview",
    "Map",
    "Trends",
    "Correlation",
    "Data",
])

# ----------------------------- OVERVIEW TAB -----------------------------
with tab_overview:
    st.subheader(f"Key metrics — {INDICATOR_LABELS[indicator]}")

    countries_filtered = countries_df[
        (countries_df["year"] >= year_range[0]) &
        (countries_df["year"] <= year_range[1])
    ].dropna(subset=[indicator])

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
        st.metric(f"Global average ({latest_year})", f"{global_mean:,.1f}")
    with col2:
        st.metric(f"Highest ({latest_year})", f"{top_row[indicator]:,.1f}")
        st.caption(top_row["country"])
    with col3:
        st.metric(f"Lowest ({latest_year})", f"{bottom_row[indicator]:,.1f}")
        st.caption(bottom_row["country"])
    with col4:
        if biggest_improver is not None:
            st.metric(
                f"Largest change ({first_year}–{latest_year})",
                f"{biggest_improver['delta']:+,.1f}",
            )
            st.caption(biggest_improver["country"])

    st.markdown("---")
    st.info(
        "Use the sidebar controls to change the indicator, time range, "
        "or countries highlighted. Switch between tabs above for different views."
    )

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
            color_continuous_scale="Viridis",
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
                colour_scale = "Greens"
            elif rank_mode == "Bottom 10":
                plot_df = rank_df.nsmallest(10, indicator)
                colour_scale = "Reds"
            else:
                top5 = rank_df.nlargest(5, indicator)
                bot5 = rank_df.nsmallest(5, indicator)
                plot_df = pd.concat([top5, bot5])
                colour_scale = "RdYlGn"

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
            color="renewable_energy_pct", color_continuous_scale="Viridis",
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
    st.write(
        f"{len(filtered):,} rows · {filtered['country'].nunique()} countries/regions"
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"se4all_filtered_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv",
    )

    st.dataframe(filtered, use_container_width=True)