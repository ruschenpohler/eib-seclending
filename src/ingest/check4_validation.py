"""Validate EIBIS and SAFE data coverage for Check 4.

Reads the downloaded EIBIS CSV files and SAFE Excel file to assess
country and year coverage.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from src.config import DATA_RAW

EU27_CODES = {
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


def load_eibis_constrain_prop():
    """Load all constrain-prop files and build country×year panel."""
    files = sorted(DATA_RAW.glob("eibis_accfin_constrain-prop_*.csv"))
    print(f"Found {len(files)} constrain-prop files")

    all_data = []
    for f in files:
        year = int(f.stem.split("_")[-1])
        df = pd.read_csv(f)
        # First column is label, rest are country codes
        # Transpose to long format
        df_long = df.iloc[0, 1:].reset_index()
        df_long.columns = ["country_code", "constrained_prop"]
        df_long["year"] = year
        all_data.append(df_long)

    if not all_data:
        return None
    return pd.concat(all_data, ignore_index=True)


def load_safe_data():
    """Load SAFE main series Excel and inspect structure."""
    safe_file = DATA_RAW / "SAFE_series_2026Q1.xlsx"
    if not safe_file.exists():
        print(f"SAFE file not found: {safe_file}")
        return None

    # Read all sheet names
    xl = pd.ExcelFile(safe_file)
    print(f"SAFE file has {len(xl.sheet_names)} sheets")
    print(f"Sheet names (first 20): {xl.sheet_names[:20]}")

    # Read first sheet to see structure
    df = pd.read_excel(safe_file, sheet_name=xl.sheet_names[0])
    print(f"\nFirst sheet shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"First 5 rows:\n{df.head()}")

    return xl


def assess_eibis_coverage(df):
    """Assess EIBIS coverage against Check 4 criteria."""
    print("\n=== EIBIS Coverage Assessment ===")
    print(f"Total observations: {len(df)}")
    print(f"Year range: {df['year'].min()}–{df['year'].max()}")
    print(f"Number of years: {df['year'].nunique()}")
    print(f"Countries covered: {sorted(df['country_code'].unique())}")
    print(f"Number of countries: {df['country_code'].nunique()}")

    # Check EU27 coverage
    eu_countries = set(df["country_code"].unique()) & EU27_CODES
    print(f"EU-27 countries covered: {len(eu_countries)} / 27")
    print(f"Missing EU-27: {sorted(EU27_CODES - eu_countries)}")

    # Country×year completeness
    country_year_counts = df.groupby("year")["country_code"].nunique()
    print("\nCountries per year:")
    print(country_year_counts)

    # Check coverage criterion: >=24/27 countries, >=7 years
    n_countries = len(eu_countries)
    n_years = df["year"].nunique()
    print("\nCheck 4 criterion: >=24/27 countries, >=7 years")
    print(f"Actual: {n_countries}/27 countries, {n_years} years")
    if n_countries >= 24 and n_years >= 7:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL — fallback to ECB SAFE")

    return n_countries, n_years


if __name__ == "__main__":
    print("=== Check 4: EIBIS and SAFE Coverage Validation ===\n")

    # EIBIS
    eibis_df = load_eibis_constrain_prop()
    if eibis_df is not None:
        n_countries, n_years = assess_eibis_coverage(eibis_df)
    else:
        print("No EIBIS data found")

    # SAFE
    print("\n" + "=" * 60)
    safe_xl = load_safe_data()
