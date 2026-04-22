"""Data loading and cleaning for the SE4ALL dashboard."""

from pathlib import Path
import pandas as pd

# Map verbose SE4ALL column names → clean, dashboard-friendly names
INDICATOR_RENAME = {
    "Access to electricity (% of total population) [1.1_ACCESS.ELECTRICITY.TOT]": "electricity_access_pct",
    "Access to Clean Fuels and Technologies for cooking (% of total population) [2.1_ACCESS.CFT.TOT]": "clean_fuels_access_pct",
    "Renewable electricity share of total electricity output (%) [4.1_SHARE.RE.IN.ELECTRICITY]": "renewable_electricity_pct",
    "Renewable energy share of TFEC (%) [2.1_SHARE.TOTAL.RE.IN.TFEC]": "renewable_energy_pct",
    "Renewable electricity output (GWh) [4.1.2_REN.ELECTRICITY.OUTPUT]": "renewable_electricity_gwh",
    "Total electricity output (GWh) [4.1.1_TOTAL.ELECTRICITY.OUTPUT]": "total_electricity_gwh",
    "Energy intensity level of primary energy (MJ/2011 USD PPP) [6.1_PRIMARY.ENERGY.INTENSITY]": "energy_intensity",
}

# Human-readable labels for the UI
INDICATOR_LABELS = {
    "electricity_access_pct": "Access to Electricity (%)",
    "clean_fuels_access_pct": "Access to Clean Cooking Fuels (%)",
    "renewable_electricity_pct": "Renewable Electricity Share (%)",
    "renewable_energy_pct": "Renewable Energy Share of TFEC (%)",
    "renewable_electricity_gwh": "Renewable Electricity Output (GWh)",
    "total_electricity_gwh": "Total Electricity Output (GWh)",
    "energy_intensity": "Energy Intensity (MJ/2011 USD PPP)",
}

# Non-country entries in the World Bank dataset (regional/income aggregates)
REGIONAL_AGGREGATES = {
    "World", "European Union", "OECD members",
    "High income", "Low income", "Middle income",
    "Upper middle income", "Lower middle income",
    "Low & middle income", "Heavily indebted poor countries (HIPC)",
    "Sub-Saharan Africa", "Sub-Saharan Africa (excluding high income)",
    "Sub-Saharan Africa (IDA & IBRD countries)",
    "East Asia & Pacific", "East Asia & Pacific (excluding high income)",
    "East Asia & Pacific (IDA & IBRD countries)",
    "Europe & Central Asia", "Europe & Central Asia (excluding high income)",
    "Europe & Central Asia (IDA & IBRD countries)",
    "Latin America & Caribbean", "Latin America & Caribbean (excluding high income)",
    "Latin America & the Caribbean (IDA & IBRD countries)",
    "Middle East & North Africa", "Middle East & North Africa (excluding high income)",
    "Middle East & North Africa (IDA & IBRD countries)",
    "North America", "South Asia", "South Asia (IDA & IBRD)",
    "Arab World", "Central Europe and the Baltics",
    "Euro area", "Fragile and conflict affected situations",
    "Least developed countries: UN classification",
    "Pacific island small states", "Small states",
    "Caribbean small states", "Other small states",
    "IDA only", "IDA blend", "IDA total", "IDA & IBRD total", "IBRD only",
    "Post-demographic dividend", "Pre-demographic dividend",
    "Early-demographic dividend", "Late-demographic dividend",
    "Not classified",
}


def load_se4all(path: str | Path = "data/se4all_raw.csv") -> pd.DataFrame:
    """Load and clean the SE4ALL dataset.

    Returns a tidy DataFrame with columns:
    country, country_code, year, is_aggregate, + 7 indicator columns.
    """
    df = pd.read_csv(path, na_values=["..", ""])

    # Drop footer rows (they have NaN Country Code)
    df = df.dropna(subset=["Country Code"]).copy()

    # Rename columns
    df = df.rename(columns=INDICATOR_RENAME)
    df = df.rename(columns={
        "Country Name": "country",
        "Country Code": "country_code",
        "Time": "year",
    })

    # Drop redundant Time Code column
    df = df.drop(columns=["Time Code"], errors="ignore")

    # Ensure correct dtypes
    df["year"] = df["year"].astype(int)
    for col in INDICATOR_RENAME.values():
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag regional aggregates vs actual countries
    df["is_aggregate"] = df["country"].isin(REGIONAL_AGGREGATES)

    return df.reset_index(drop=True)


def get_countries_only(df: pd.DataFrame) -> pd.DataFrame:
    """Return only actual countries, excluding regional/income aggregates."""
    return df[~df["is_aggregate"]].copy()


def get_aggregates_only(df: pd.DataFrame) -> pd.DataFrame:
    """Return only regional/income aggregates."""
    return df[df["is_aggregate"]].copy()