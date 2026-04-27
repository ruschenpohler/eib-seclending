"""Check 1 inspection script for EIB Projects Financed dataset.

Reads the manually provided loanExport.xlsx and runs sub-tasks 1a, 1b, 1c.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from src.config import DATA_RAW


def main():
    path = DATA_RAW / "loanExport.xlsx"
    df = pd.read_excel(path, engine="openpyxl")

    print("=" * 60)
    print("CHECK 1a — Schema and variable semantics")
    print("=" * 60)
    print(f"File: {path}")
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    print()

    # Parse dates
    df["signature_date"] = pd.to_datetime(
        df["Signature Date"], format="%d/%m/%Y", errors="coerce"
    )
    n_bad_dates = df["signature_date"].isna().sum()
    print(f"Date parsing: {n_bad_dates} NaT out of {len(df)} rows")

    # Year range
    years = df["signature_date"].dt.year.dropna().astype(int)
    print(f"Year range: {years.min()} – {years.max()}")
    print(f"Years present: {sorted(years.unique())}")
    print()

    # Signed Amount
    print("Signed Amount — first 10 samples:")
    for i, val in enumerate(df["Signed Amount"].dropna().head(10), 1):
        print(f"  {i}: {repr(val)}")
    print()

    print("=" * 60)
    print("CHECK 1b — Year coverage")
    print("=" * 60)
    year_counts = years.value_counts().sort_index()
    print(year_counts.to_string())
    print()

    print("=" * 60)
    print("CHECK 1c — NUTS-2 geographic coverage")
    print("=" * 60)
    region_pop = df["Region"].notna().sum()
    print(
        f"Region field populated: {region_pop:,} / {len(df):,} ({region_pop/len(df)*100:.1f}%)"
    )
    print(f"Unique regions: {df['Region'].nunique()}")
    print()
    print("Region value counts (top 10):")
    print(df["Region"].value_counts().head(10).to_string())
    print()

    print("=" * 60)
    print("Sector / intermediated operations (MBIL) check")
    print("=" * 60)
    print(f"Unique sectors: {df['Sector'].nunique()}")
    print("Sector value counts:")
    print(df["Sector"].value_counts().to_string())
    print()

    print("=" * 60)
    print("EU coverage")
    print("=" * 60)
    eu_mask = df["Region"] == "European Union"
    eu_df = df[eu_mask]
    eu_countries = eu_df["Country or Territory"].value_counts()
    print(
        f"EU rows: {eu_countries.nunique()} countries, {eu_countries.sum():,} projects"
    )
    print(eu_countries.to_string())
    print()

    print("=" * 60)
    print("SUMMARY FOR IMPL-LOG")
    print("=" * 60)
    print(f"Rows: {len(df):,}")
    print(f"Year range: {years.min()} – {years.max()}")
    print(f"EU countries: {eu_countries.nunique()}")
    print(f"Sectors: {df['Sector'].nunique()}")
    print(f"Region field: {region_pop/len(df)*100:.1f}% populated")


if __name__ == "__main__":
    main()
