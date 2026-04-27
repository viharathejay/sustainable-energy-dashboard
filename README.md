# Sustainable Energy for All — Interactive Dashboard

An interactive Streamlit dashboard exploring the World Bank's [Sustainable Energy for All (SE4ALL)](https://databank.worldbank.org/source/sustainable-energy-for-all) dataset. Built as the individual coursework submission for **5DATA004W Data Science Project Lifecycle** at the University of Westminster (2025/26).

The dashboard transforms 4,250 rows of country-year energy data into five complementary analytical views, supporting decision-makers exploring global progress toward UN Sustainable Development Goal 7 — affordable and clean energy.

---

## Live demo

**Streamlit app:** [https://sustainable-energy-vihara.streamlit.app](https://sustainable-energy-vihara.streamlit.app)

---

## Features

- **Overview** — KPI cards (global average, highest, lowest, biggest improver) plus a compact world map and global trend area chart
- **Map** — full-size choropleth with year slider for time-based exploration
- **Trends** — multi-country time-series line chart and configurable rankings bar chart (Top 10 / Bottom 10 / Top & Bottom 5)
- **Correlation** — scatter plot with OLS trendline and Pearson correlation coefficient between any two indicators
- **Data** — filtered raw data table with one-click CSV export

Sidebar controls for year range, primary indicator, country highlights, and regional aggregate toggle drive every view.

---

## Dataset

**Source:** World Bank DataBank — Sustainable Energy for All
**Coverage:** 217 countries plus regional/income aggregates, 2000–2016
**Indicators (7):** access to electricity, access to clean cooking fuels, renewable electricity share, renewable energy share of TFEC, renewable electricity output (GWh), total electricity output (GWh), energy intensity

The raw CSV is included at `data/se4all_raw.csv` so the app is fully self-contained.

---

## Tech stack

- **Streamlit** — application framework
- **pandas** — data manipulation
- **Plotly Express** — interactive visualisations
- **statsmodels** — OLS regression for correlation trendline
- **GitHub** + **Streamlit Community Cloud** — version control and deployment

---

## Project structure

```
