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
    page_icon="⚡",
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
st.sidebar.title("⚡ Controls")

# Year range slider
year_min, year_max = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1,
)

# Indicator selector
indicator_options = list(INDICATOR_LABELS.keys())
indicator = st.sidebar.selectbox(
    "Primary indicator",
    options=indicator_options,
    format_func=lambda x: INDICATOR_LABELS[x],
    index=0,
)

# Country multiselect — default to a few interesting picks
default_countries = ["United Kingdom", "United States", "India", "China", "Germany", "Brazil"]
available_countries = sorted(countries_df["country"].unique())
selected_countries = st.sidebar.multiselect(
    "Countries to highlight",
    options=available_countries,
    default=[c for c in default_countries if c in available_countries],
)

# Toggle: include/exclude regional aggregates
show_aggregates = st.sidebar.checkbox(
    "Include regional aggregates (World, EU, etc.)",
    value=False,
    help="Includes entries like 'World', 'European Union', income groups.",
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data source: World Bank — Sustainable Energy for All (SE4ALL). "
    "[Open in DataBank ↗](https://databank.worldbank.org/source/sustainable-energy-for-all)"
)

# ---------------------------------------------------------------------
# Filter data based on sidebar
# ---------------------------------------------------------------------
base_df = df if show_aggregates else countries_df
filtered = base_df[
    (base_df["year"] >= year_range[0]) & (base_df["year"] <= year_range[1])
].copy()

# ---------------------------------------------------------------------
# Main page — header
# ---------------------------------------------------------------------
st.title("⚡ Sustainable Energy for All — Global Dashboard")
st.caption(
    "5DATA004W Individual Coursework — Vihara Thejaka Kularathna (W2053281) · "
    f"Showing data for {year_range[0]}–{year_range[1]} · "
    "Data: World Bank SE4ALL"
)

# ---------------------------------------------------------------------
# KPI cards — headline numbers for the selected indicator
# ---------------------------------------------------------------------
st.subheader(f"📊 Key metrics — {INDICATOR_LABELS[indicator]}")

# Use only country-level rows (not aggregates) for these stats regardless
# of the sidebar toggle, so the leaderboard isn't polluted by "World" etc.
countries_filtered = countries_df[
    (countries_df["year"] >= year_range[0]) &
    (countries_df["year"] <= year_range[1])
].dropna(subset=[indicator])

latest_year = int(countries_filtered["year"].max())
latest_snapshot = countries_filtered[countries_filtered["year"] == latest_year]

# Compute KPIs
global_mean = latest_snapshot[indicator].mean()
top_row = latest_snapshot.nlargest(1, indicator).iloc[0]
bottom_row = latest_snapshot.nsmallest(1, indicator).iloc[0]

# Biggest improver over the selected range
first_year = int(countries_filtered["year"].min())
start_snapshot = countries_filtered[countries_filtered["year"] == first_year][["country", indicator]]
end_snapshot = latest_snapshot[["country", indicator]]
change = end_snapshot.merge(
    start_snapshot, on="country", suffixes=("_end", "_start")
)
change["delta"] = change[f"{indicator}_end"] - change[f"{indicator}_start"]
biggest_improver = change.nlargest(1, "delta").iloc[0] if len(change) else None

# Render 4 cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label=f"Global average ({latest_year})",
        value=f"{global_mean:,.1f}",
    )

with col2:
    st.metric(
        label=f"🥇 Highest ({latest_year})",
        value=f"{top_row[indicator]:,.1f}",
        help=top_row["country"],
    )
    st.caption(top_row["country"])

with col3:
    st.metric(
        label=f"🔻 Lowest ({latest_year})",
        value=f"{bottom_row[indicator]:,.1f}",
        help=bottom_row["country"],
    )
    st.caption(bottom_row["country"])

with col4:
    if biggest_improver is not None:
        st.metric(
            label=f"📈 Biggest improver ({first_year}→{latest_year})",
            value=f"+{biggest_improver['delta']:,.1f}",
            help=biggest_improver["country"],
        )
        st.caption(biggest_improver["country"])
    else:
        st.metric(label="Biggest improver", value="—")

st.markdown("---")

# ---------------------------------------------------------------------
# Data preview (kept for now, will be replaced by charts in Layer 3+)
# ---------------------------------------------------------------------
st.subheader("Filtered data preview")
st.write(
    f"**{len(filtered):,}** rows · "
    f"**{filtered['country'].nunique()}** countries/regions"
)
st.dataframe(
    filtered[["country", "year", indicator]]
    .dropna(subset=[indicator])
    .sort_values([indicator], ascending=False)
    .head(20),
    use_container_width=True,
)
# ---------------------------------------------------------------------
# Choropleth world map — spatial view of the selected indicator
# ---------------------------------------------------------------------
st.subheader(f"🗺️ Global map — {INDICATOR_LABELS[indicator]}")

# Year picker for the map (defaults to the latest year in range)
map_year = st.slider(
    "Map year",
    min_value=year_range[0],
    max_value=year_range[1],
    value=year_range[1],
    step=1,
    key="map_year",
)

map_df = countries_df[
    (countries_df["year"] == map_year)
].dropna(subset=[indicator])

if len(map_df) == 0:
    st.warning(f"No data available for {map_year}. Try a different year.")
else:
    fig_map = px.choropleth(
        map_df,
        locations="country_code",
        color=indicator,
        hover_name="country",
        hover_data={
            "country_code": False,
            indicator: ":,.2f",
        },
        color_continuous_scale="Viridis",
        labels={indicator: INDICATOR_LABELS[indicator]},
        title=f"{INDICATOR_LABELS[indicator]} — {map_year}",
    )
    fig_map.update_layout(
        height=550,
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(
        f"Showing {len(map_df)} countries with data for {map_year}. "
        "Hover over countries for exact values."
    )