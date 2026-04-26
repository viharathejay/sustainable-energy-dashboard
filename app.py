"""
Sustainable Energy for All — Interactive Dashboard.


Author:    Vihara Thejaka Kularathna
Student:   W2053281

"""

# Imports
import streamlit as st
import pandas as pd
import plotly.express as px

# Local module: data loading and cleaning helpers
from src.data_loader import (
    load_se4all,
    get_countries_only,
    INDICATOR_LABELS,
)


# Page configuration — must be the first Streamlit call in the script.
st.set_page_config(
    page_title="Sustainable Energy Dashboard",
    layout="wide",                       # use full browser width for charts
    initial_sidebar_state="expanded",    # show sidebar by default
)


# Design tokens — centralised palette so any colour change propagates everywhere.

# Brand palette
PRIMARY = "#14B8A6"          # teal — primary brand colour
PRIMARY_DARK = "#0F766E"     # darker teal — used for emphasis / hover

# KPI accent colours (one per card to aid quick scanning)
ACCENT_AMBER = "#F59E0B"     # global average
ACCENT_EMERALD = "#10B981"   # highest performer
ACCENT_ROSE = "#EC4899"      # lowest performer
ACCENT_VIOLET = "#8B5CF6"    # largest change

# Neutrals
INK = "#0F172A"              # primary heading text
MUTED = "#64748B"            # secondary text and captions
BG_SOFT = "#F8FAFC"          # page background
BORDER = "#E2E8F0"           # card and divider borders

# Plotly chart palettes
SEQUENTIAL_SCALE = "Tealgrn"                       # single-metric maps and bars
DIVERGING_SCALE = "RdYlGn"                         # top-vs-bottom comparisons
QUALITATIVE_PALETTE = px.colors.qualitative.Safe   # colour-blind friendly lines


# Custom CSS — Inter font, KPI card styling, tab and section polish.
# Injected once at the top so all subsequent components inherit the styles.
st.markdown(
    """
    <style>
    /* Import Inter — modern geometric sans-serif used by major SaaS apps */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Apply Inter globally to all Streamlit-rendered text */
    html, body, [class*="css"], .stMarkdown, .stText {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    /* KPI card — white card with icon, label, value, sub-caption */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 1px 3px rgba(15,23,42,0.04),
                    0 4px 12px rgba(15,23,42,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
    }
    /* Subtle lift on hover so the cards feel interactive */
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 6px rgba(15,23,42,0.06),
                    0 10px 20px rgba(15,23,42,0.05);
    }

    /* Coloured circle holding the SVG icon on each KPI card */
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

    /* Tab labels — slightly larger and lighter weight than default */
    button[data-baseweb="tab"] {
        font-weight: 500 !important;
        padding: 0.6rem 1rem !important;
    }

    /* Compact section heading used inside tabs */
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


# Data loading — wrapped in @st.cache_data so the CSV is read and cleaned
# only once per session (not on every widget interaction). This is a major
# performance optimisation for the dashboard.
@st.cache_data
def get_data() -> pd.DataFrame:
    """Load and clean the SE4ALL dataset. Cached for the session."""
    return load_se4all()


# Two views of the same data:
#   df            — everything (countries plus regional/income aggregates)
#   countries_df  — actual countries only (used for rankings, KPIs, etc.)
df = get_data()
countries_df = get_countries_only(df)


# Sidebar — global filters that drive every tab.
st.sidebar.title("Controls")

# Year range slider (defines the time-window of all visualisations)
year_min, year_max = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1,
)

# Primary indicator selector. INDICATOR_LABELS maps internal column names
# (e.g. "electricity_access_pct") to user-facing labels (e.g. "Access to Electricity (%)").
indicator_options = list(INDICATOR_LABELS.keys())
indicator = st.sidebar.selectbox(
    "Primary indicator",
    options=indicator_options,
    format_func=lambda x: INDICATOR_LABELS[x],
    index=0,
)

# Country highlight multiselect — used by the Trends tab for time-series comparison.
default_countries = [
    "United Kingdom", "United States", "India",
    "China", "Germany", "Brazil",
]
available_countries = sorted(countries_df["country"].unique())
selected_countries = st.sidebar.multiselect(
    "Countries to highlight",
    options=available_countries,
    default=[c for c in default_countries if c in available_countries],
)

# Aggregate toggle — off by default so rankings/maps focus on individual countries.
show_aggregates = st.sidebar.checkbox(
    "Include regional aggregates (World, EU, etc.)",
    value=False,
    help="Includes entries like 'World', 'European Union', income groups.",
)

# Data source attribution at the foot of the sidebar
st.sidebar.markdown("---")
st.sidebar.caption(
    "Data source: World Bank — Sustainable Energy for All (SE4ALL). "
    "[Open in DataBank](https://databank.worldbank.org/source/sustainable-energy-for-all)"
)


# Page header — title and dynamic caption that reflects the current filters.
st.title("Sustainable Energy for All — Global Dashboard")
st.caption(
    "5DATA004W Individual Coursework — Vihara Thejaka Kularathna (W2053281) · "
    f"Showing data for {year_range[0]}–{year_range[1]} · "
    "Data: World Bank SE4ALL"
)

# Apply sidebar filters to the dataset. Each tab adds its own per-indicator
# filtering (e.g. dropping NaN rows for the selected metric).
base_df = df if show_aggregates else countries_df
filtered = base_df[
    (base_df["year"] >= year_range[0]) & (base_df["year"] <= year_range[1])
].copy()


# KPI card icons — inline SVGs from Lucide (open-source, MIT-licensed).
# Stroke colour set to white so they sit cleanly on the coloured icon circle.
ICON_GLOBE = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" '
    'stroke="white" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="10"/>'
    '<path d="M2 12h20"/>'
    '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 '
    '15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'
    '</svg>'
)
ICON_TROPHY = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" '
    'stroke="white" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round">'
    '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>'
    '<path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>'
    '<path d="M4 22h16"/>'
    '<path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>'
    '<path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>'
    '<path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>'
    '</svg>'
)
ICON_TREND_DOWN = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" '
    'stroke="white" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round">'
    '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/>'
    '<polyline points="16 17 22 17 22 11"/>'
    '</svg>'
)
ICON_TREND_UP = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" '
    'stroke="white" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round">'
    '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
    '<polyline points="16 7 22 7 22 13"/>'
    '</svg>'
)


def kpi_card(icon_svg: str, icon_bg: str, label: str,
             value: str, sub: str = "") -> str:
    """Return KPI card HTML. Built as a single concatenated string so
    Streamlit's markdown renderer doesn't accidentally treat indented
    lines as a code block.
    """
    # Empty sub still renders a non-breaking space so all cards have
    # equal height in the four-column layout.
    sub_block = (
        f'<div class="kpi-sub">{sub}</div>' if sub
        else '<div class="kpi-sub">&nbsp;</div>'
    )
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-icon" style="background: {icon_bg};">{icon_svg}</div>'
        f'<div class="kpi-body">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{sub_block}'
        f'</div></div>'
    )


# Tabs — five complementary views, each focused on a specific analytical question.
tab_overview, tab_map, tab_trends, tab_corr, tab_data = st.tabs([
    "Overview", "Map", "Trends", "Correlation", "Data",
])


# Overview tab — KPIs at the top, then a compact world map and global trend
# area chart side-by-side. Acts as an executive summary of the chosen indicator.
with tab_overview:
    st.markdown(
        f'<div class="section-title">Key metrics — {INDICATOR_LABELS[indicator]}</div>',
        unsafe_allow_html=True,
    )

    # Restrict to country-level rows for fair "leaderboard" stats.
    countries_filtered = countries_df[
        (countries_df["year"] >= year_range[0]) &
        (countries_df["year"] <= year_range[1])
    ].dropna(subset=[indicator])

    if len(countries_filtered) > 0:
        # Latest-year snapshot — used for "global average", "highest", "lowest"
        latest_year = int(countries_filtered["year"].max())
        latest_snapshot = countries_filtered[
            countries_filtered["year"] == latest_year
        ]

        global_mean = latest_snapshot[indicator].mean()
        top_row = latest_snapshot.nlargest(1, indicator).iloc[0]
        bottom_row = latest_snapshot.nsmallest(1, indicator).iloc[0]

        # Largest change calculation: difference between the first and last
        # year of the selected range, computed per country.
        first_year = int(countries_filtered["year"].min())
        start_snapshot = countries_filtered[
            countries_filtered["year"] == first_year
        ][["country", indicator]]
        end_snapshot = latest_snapshot[["country", indicator]]
        change = end_snapshot.merge(
            start_snapshot, on="country", suffixes=("_end", "_start")
        )
        change["delta"] = change[f"{indicator}_end"] - change[f"{indicator}_start"]
        biggest_improver = (
            change.nlargest(1, "delta").iloc[0] if len(change) else None
        )

        # Render the four KPI cards in a row.
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                kpi_card(
                    ICON_GLOBE, ACCENT_AMBER,
                    f"Global average · {latest_year}",
                    f"{global_mean:,.1f}",
                ),
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                kpi_card(
                    ICON_TROPHY, ACCENT_EMERALD,
                    f"Highest · {latest_year}",
                    f"{top_row[indicator]:,.1f}",
                    top_row["country"],
                ),
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                kpi_card(
                    ICON_TREND_DOWN, ACCENT_ROSE,
                    f"Lowest · {latest_year}",
                    f"{bottom_row[indicator]:,.1f}",
                    bottom_row["country"],
                ),
                unsafe_allow_html=True,
            )
        with col4:
            if biggest_improver is not None:
                st.markdown(
                    kpi_card(
                        ICON_TREND_UP, ACCENT_VIOLET,
                        f"Largest change · {first_year}–{latest_year}",
                        f"{biggest_improver['delta']:+,.1f}",
                        biggest_improver["country"],
                    ),
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # Two-column preview row beneath the KPIs.
        ov_col1, ov_col2 = st.columns(2)

        # Compact choropleth showing geographic distribution at the latest year.
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
                geo=dict(
                    showframe=False, showcoastlines=True,
                    projection_type="natural earth",
                ),
                coloraxis_colorbar=dict(thickness=10, len=0.7, title=None),
            )
            st.plotly_chart(ov_map, use_container_width=True)

        # Global trend — annual mean of the selected indicator across all countries.
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
            "For deeper analysis, see the Map, Trends, and Correlation tabs."
        )

    else:
        st.warning("No data available for this filter combination.")


# Map tab — full-width choropleth with its own year slider for animation-style
# exploration. Clicking through years reveals how electrification or renewable
# adoption spread over time.
with tab_map:
    st.subheader(f"Global map — {INDICATOR_LABELS[indicator]}")

    # Map-specific year slider (separate from sidebar so users can scrub
    # through years without changing the global filter).
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
            geo=dict(
                showframe=False, showcoastlines=True,
                projection_type="natural earth",
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption(
            f"Showing {len(map_df)} countries with data for {map_year}. "
            "Hover over countries for exact values."
        )


# Trends tab — two complementary chart types stacked vertically:
#   1. Time-series line chart of selected countries
#   2. Country rankings bar chart for a single year
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
                labels={
                    "year": "Year",
                    indicator: INDICATOR_LABELS[indicator],
                    "country": "Country",
                },
                title=f"{INDICATOR_LABELS[indicator]} · {year_range[0]}–{year_range[1]}",
            )
            fig_ts.update_layout(
                height=500,
                hovermode="x unified",   # show all country values at one year
                legend=dict(
                    orientation="h", yanchor="bottom",
                    y=-0.25, xanchor="center", x=0.5,
                ),
                margin=dict(l=0, r=0, t=50, b=0),
            )
            fig_ts.update_traces(line=dict(width=2.5))
            st.plotly_chart(fig_ts, use_container_width=True)

            # Auto-generated insight caption — surfaces the largest mover among
            # the selected countries so the reader has a ready takeaway.
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

    # Two-column layout: controls on the left (narrow), chart on the right.
    rank_col1, rank_col2 = st.columns([1, 3])
    with rank_col1:
        rank_year = st.slider(
            "Ranking year",
            min_value=year_range[0], max_value=year_range[1],
            value=year_range[1], step=1, key="rank_year",
        )
        rank_mode = st.radio(
            "Show",
            options=["Top 10", "Bottom 10", "Top & Bottom 5"],
            index=0,
        )

    with rank_col2:
        rank_df = countries_df[
            countries_df["year"] == rank_year
        ].dropna(subset=[indicator])

        if len(rank_df) > 0:
            # Each ranking mode uses a colour scale that matches its semantic:
            # green for "best", red for "worst", diverging for "compare both ends".
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
                title=f"{rank_mode} — {rank_year}",
                text=indicator,
            )
            fig_bar.update_traces(
                texttemplate="%{text:.1f}", textposition="outside",
            )
            fig_bar.update_layout(
                height=450,
                margin=dict(l=0, r=0, t=50, b=0),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_bar, use_container_width=True)


# Correlation tab — scatter plot for examining whether two indicators move
# together. OLS trendline and Pearson coefficient quantify the relationship.
with tab_corr:
    st.subheader("Indicator correlation")
    st.caption(
        "Explore whether two indicators move together. "
        "Each point represents one country for the selected year."
    )

    # Independent X and Y indicator pickers for free pairwise exploration.
    scatter_col1, scatter_col2 = st.columns(2)
    with scatter_col1:
        x_indicator = st.selectbox(
            "X-axis indicator", options=indicator_options,
            format_func=lambda x: INDICATOR_LABELS[x],
            index=0, key="x_indicator",
        )
    with scatter_col2:
        y_indicator = st.selectbox(
            "Y-axis indicator", options=indicator_options,
            format_func=lambda x: INDICATOR_LABELS[x],
            index=3, key="y_indicator",
        )

    scatter_year = st.slider(
        "Year",
        min_value=year_range[0], max_value=year_range[1],
        value=year_range[1], step=1, key="scatter_year",
    )

    # Drop any country missing one of the three plotted variables so Plotly
    # has clean numeric data for both axes plus the bubble-size dimension.
    scatter_df = countries_df[
        countries_df["year"] == scatter_year
    ].dropna(subset=[x_indicator, y_indicator, "total_electricity_gwh"])

    if x_indicator == y_indicator:
        st.info(
            "Select two different indicators on the X and Y axes "
            "to examine a relationship."
        )
    elif len(scatter_df) < 10:
        st.warning(f"Not enough data points for {scatter_year}.")
    else:
        fig_scatter = px.scatter(
            scatter_df,
            x=x_indicator, y=y_indicator, hover_name="country",
            size="total_electricity_gwh",   # bubble size encodes scale
            size_max=40,
            color="renewable_energy_pct",   # colour encodes renewable share
            color_continuous_scale=SEQUENTIAL_SCALE,
            labels={
                x_indicator: INDICATOR_LABELS[x_indicator],
                y_indicator: INDICATOR_LABELS[y_indicator],
                "renewable_energy_pct": "Renewable %",
                "total_electricity_gwh": "Total electricity (GWh)",
            },
            title=f"{INDICATOR_LABELS[y_indicator]} vs {INDICATOR_LABELS[x_indicator]} — {scatter_year}",
            trendline="ols",   # ordinary least squares regression line
        )
        fig_scatter.update_layout(
            height=550, margin=dict(l=0, r=0, t=50, b=0),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Quantify the relationship with a Pearson correlation coefficient.
        # Threshold bands follow common interpretive convention.
        correlation = scatter_df[x_indicator].corr(scatter_df[y_indicator])
        corr_strength = (
            "strong" if abs(correlation) > 0.7
            else "moderate" if abs(correlation) > 0.4
            else "weak"
        )
        corr_direction = "positive" if correlation > 0 else "negative"
        st.caption(
            f"Pearson correlation: {correlation:+.2f} — "
            f"a {corr_strength} {corr_direction} relationship. "
            "Bubble size represents total electricity output; "
            "colour represents renewable energy share."
        )


# Data tab — raw filtered dataset with CSV download. Lets analysts inspect
# the underlying numbers and export them for offline use.
with tab_data:
    st.subheader("Filtered data")
    st.write(
        f"{len(filtered):,} rows · "
        f"{filtered['country'].nunique()} countries/regions"
    )

    # CSV download — encoded as bytes for st.download_button compatibility.
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"se4all_filtered_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv",
    )

    st.dataframe(filtered, use_container_width=True)