"""Build the Phase 1 analysis dataset.

Merges:
- EIB Projects (country×year signed amounts)
- SAFE constraints (country×year access-to-finance share)
- Eurostat SBS (SME counts, employment, value added)
- Eurostat BD (enterprise births, active stock)
- Eurostat GDP per capita

Outputs:
- data/processed/eib_analysis.duckdb

Before proceeding, answers three conceptual grounding questions
from AGENTS.md in the implementation log.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import duckdb
import pandas as pd

from src.config import DATA_RAW, DATA_INTERIM, DATA_PROCESSED

# Country name -> ISO code mapping for EIB Projects
EIB_COUNTRY_MAP = {
    "austria": "AT",
    "belgium": "BE",
    "bulgaria": "BG",
    "croatia": "HR",
    "cyprus": "CY",
    "czech republic": "CZ",
    "czechia": "CZ",
    "denmark": "DK",
    "estonia": "EE",
    "finland": "FI",
    "france": "FR",
    "germany": "DE",
    "greece": "EL",
    "hungary": "HU",
    "ireland": "IE",
    "italy": "IT",
    "latvia": "LV",
    "lithuania": "LT",
    "luxembourg": "LU",
    "malta": "MT",
    "netherlands": "NL",
    "the netherlands": "NL",
    "poland": "PL",
    "portugal": "PT",
    "romania": "RO",
    "slovakia": "SK",
    "slovenia": "SI",
    "spain": "ES",
    "sweden": "SE",
    # Exclude non-EU and aggregates
    "united kingdom": None,
    "norway": None,
    "switzerland": None,
    "iceland": None,
    "serbia": None,
    "montenegro": None,
    "north macedonia": None,
    "albania": None,
    "bosnia and herzegovina": None,
    "kosovo": None,
    "turkey": None,
    "moldova": None,
    "ukraine": None,
    "eu countries": None,  # generic pan-EU — excluded
}

EU27 = {
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "EL",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
}


def load_eib_projects() -> pd.DataFrame:
    """Load and aggregate EIB Projects signed amounts to country×year."""
    print("Loading EIB Projects...")
    df = pd.read_excel(DATA_RAW / "loanExport.xlsx", engine="openpyxl")

    # Clean amount: remove Euro symbol, commas, spaces
    import re

    df["signed_amount"] = (
        df["Signed Amount"]
        .fillna("")
        .astype(str)
        .apply(lambda x: re.sub(r"[^0-9.,]", "", x))
        .str.replace(",", "", regex=False)
        .replace("", pd.NA)
        .pipe(pd.to_numeric, errors="coerce")
    )

    # Clean date and extract year
    df["signature_date"] = pd.to_datetime(
        df["Signature Date"], format="%d/%m/%Y", errors="coerce"
    )
    df["year"] = df["signature_date"].dt.year

    # Map country
    df["country_raw"] = df["Country or Territory"].str.lower().str.strip()
    df["country"] = df["country_raw"].map(EIB_COUNTRY_MAP)

    # Drop non-EU and missing
    n_total = len(df)
    df = df[df["country"].notna()]
    df = df[df["country"].isin(EU27)]
    n_dropped = n_total - len(df)
    print(f"  Dropped {n_dropped} rows (non-EU, generic, or unmapped)")

    # Aggregate to country×year
    agg = (
        df.groupby(["country", "year"])["signed_amount"]
        .sum()
        .reset_index()
        .rename(columns={"signed_amount": "eib_signed_amount"})
    )
    print(f"  Country×year observations: {len(agg)}")
    print(f"  Year range: {agg['year'].min()}-{agg['year'].max()}")
    return agg


def load_safe_constraints() -> pd.DataFrame:
    """Load SAFE constraint panel."""
    print("Loading SAFE constraints...")
    df = pd.read_csv(DATA_INTERIM / "safe_constraint_panel.csv")
    print(f"  Observations: {len(df)}")
    print(f"  Year range: {df['year'].min()}-{df['year'].max()}")
    return df


def load_sbs_sca() -> pd.DataFrame:
    """Load Eurostat SBS size-class data and aggregate to country×year."""
    print("Loading Eurostat SBS (size-class)...")
    df = pd.read_csv(DATA_RAW / "eurostat_sbs_sc_sca_r2.csv")

    # Aggregate size classes 10-19, 20-49, 50-249 to total SME (10-249)
    df["time_period"] = df["time_period"].astype(int)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    agg = df.groupby(["geo", "time_period", "indic_sb"])["value"].sum().reset_index()

    # Pivot to wide
    wide = agg.pivot_table(
        index=["geo", "time_period"],
        columns="indic_sb",
        values="value",
    ).reset_index()
    wide = wide.rename(
        columns={
            "V11110": "sme_enterprises",
            "V12110": "sme_value_added",
            "V16110": "sme_employment",
            "geo": "country",
            "time_period": "year",
        }
    )
    print(f"  Observations: {len(wide)}")
    return wide


def load_sbs_na_ind() -> pd.DataFrame:
    """Load Eurostat SBS national accounts (industry only, B,C,D,E)."""
    print("Loading Eurostat SBS (national accounts, industry)...")
    df = pd.read_csv(DATA_RAW / "eurostat_sbs_na_ind_r2.csv")
    df["time_period"] = df["time_period"].astype(int)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Aggregate NACE B,C,D,E to total industry
    agg = df.groupby(["geo", "time_period", "indic_sb"])["value"].sum().reset_index()

    wide = agg.pivot_table(
        index=["geo", "time_period"],
        columns="indic_sb",
        values="value",
    ).reset_index()
    wide = wide.rename(
        columns={
            "V15110": "industry_gross_investment",
            "V12110": "industry_value_added",
            "geo": "country",
            "time_period": "year",
        }
    )
    print(f"  Observations: {len(wide)}")
    return wide


def load_business_demography() -> pd.DataFrame:
    """Load Eurostat business demography."""
    print("Loading Eurostat business demography...")
    df = pd.read_csv(DATA_RAW / "eurostat_bd_9bd_sz_cl_r2.csv")
    df["time_period"] = df["time_period"].astype(int)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    wide = df.pivot_table(
        index=["geo", "time_period"],
        columns="indic_sb",
        values="value",
    ).reset_index()
    wide = wide.rename(
        columns={
            "V11910": "active_enterprises",
            "V11920": "enterprise_births",
            "geo": "country",
            "time_period": "year",
        }
    )
    print(f"  Observations: {len(wide)}")
    return wide


def load_gdp_per_capita() -> pd.DataFrame:
    """Load Eurostat GDP per capita."""
    print("Loading Eurostat GDP per capita...")
    df = pd.read_csv(DATA_RAW / "eurostat_nama_10_pc.csv")
    df["time_period"] = df["time_period"].astype(int)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.rename(
        columns={
            "geo": "country",
            "time_period": "year",
            "value": "gdp_per_capita",
        }
    )
    # Drop EU aggregate
    df = df[~df["country"].str.startswith("EU")]
    print(f"  Observations: {len(df)}")
    return df[["country", "year", "gdp_per_capita"]]


def build_dataset() -> pd.DataFrame:
    """Merge all sources into country×year panel."""
    print("\n=== Building analysis dataset ===\n")

    eib = load_eib_projects()
    safe = load_safe_constraints()
    sbs_sca = load_sbs_sca()
    sbs_na = load_sbs_na_ind()
    bd = load_business_demography()
    gdp = load_gdp_per_capita()

    # Start with EIB as left table (defines the temporal scope)
    # But actually we want the intersection of all data sources
    # Start with country×year grid from SAFE (2015-2021)
    panel = safe.copy()

    # Merge EIB
    panel = panel.merge(eib, on=["country", "year"], how="left")
    print(f"\nAfter EIB merge: {len(panel)} rows")

    # Merge SBS size-class
    panel = panel.merge(sbs_sca, on=["country", "year"], how="left")
    print(f"After SBS SCA merge: {len(panel)} rows")

    # Merge SBS industry
    panel = panel.merge(sbs_na, on=["country", "year"], how="left")
    print(f"After SBS NA merge: {len(panel)} rows")

    # Merge BD
    panel = panel.merge(bd, on=["country", "year"], how="left")
    print(f"After BD merge: {len(panel)} rows")

    # Merge GDP
    panel = panel.merge(gdp, on=["country", "year"], how="left")
    print(f"After GDP merge: {len(panel)} rows")

    # Compute derived variables
    # EIB volume per SME
    panel["eib_per_sme"] = panel["eib_signed_amount"] / panel["sme_enterprises"]

    # SME investment rate (industry only, V15110/V12110)
    panel["industry_investment_rate"] = (
        panel["industry_gross_investment"] / panel["industry_value_added"]
    )

    # Firm entry rate (births / active stock)
    panel["firm_entry_rate"] = panel["enterprise_births"] / panel["active_enterprises"]

    # Log transforms
    panel["log_eib_per_sme"] = np.log(panel["eib_per_sme"])
    panel["log_gdp_per_capita"] = np.log(panel["gdp_per_capita"])

    return panel


if __name__ == "__main__":
    import numpy as np

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    panel = build_dataset()

    # Save to DuckDB
    db_path = DATA_PROCESSED / "eib_analysis.duckdb"
    with duckdb.connect(str(db_path)) as con:
        con.execute("DROP TABLE IF EXISTS panel")
        con.execute("CREATE TABLE panel AS SELECT * FROM panel")
        print(f"\nSaved to {db_path}")

    # Also save to CSV for inspection
    csv_path = DATA_PROCESSED / "eib_analysis_panel.csv"
    panel.to_csv(csv_path, index=False)
    print(f"Saved to {csv_path}")

    # Coverage summary
    print("\n=== Panel coverage ===")
    print(f"Total observations: {len(panel)}")
    print(f"Countries: {panel['country'].nunique()}")
    print(f"Years: {sorted(panel['year'].unique())}")
    print("\nNon-missing rates:")
    for col in [
        "eib_signed_amount",
        "access_to_finance_share",
        "sme_enterprises",
        "industry_gross_investment",
        "enterprise_births",
        "gdp_per_capita",
    ]:
        nm = panel[col].notna().sum()
        print(f"  {col}: {nm}/{len(panel)} ({nm/len(panel)*100:.1f}%)")
