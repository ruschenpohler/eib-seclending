"""Deep inspection of EIB Projects amounts and credit lines."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from src.config import DATA_RAW


def main():
    path = DATA_RAW / "loanExport.xlsx"
    df = pd.read_excel(path, engine="openpyxl")

    # Check amount currency symbol
    print("Amount encoding check:")
    amt = df["Signed Amount"].iloc[0]
    print(f"First char: {repr(amt[0])}")
    print(f"First char bytes: {amt[0].encode('utf-8')}")
    print()

    # Clean amount
    df["signature_date"] = pd.to_datetime(
        df["Signature Date"], format="%d/%m/%Y", errors="coerce"
    )
    df["amount_clean"] = (
        df["Signed Amount"].str.replace(r"[^\d]", "", regex=True).astype(float)
    )

    print(
        f"2023 total signed amount: €{df[df['signature_date'].dt.year == 2023]['amount_clean'].sum():,.0f}"
    )
    print(f"All-time total: €{df['amount_clean'].sum():,.0f}")
    print()

    # Credit lines = intermediated?
    credit = df[df["Sector"] == "Credit lines"]
    print(f"Credit lines rows: {len(credit):,}")
    print("Credit lines by region:")
    print(credit["Region"].value_counts().to_string())
    print()
    print("Credit lines by country (top 10):")
    print(credit["Country or Territory"].value_counts().head(10).to_string())
    print()

    # EU Countries generic entry
    eu_generic = df[df["Country or Territory"] == "EU Countries"]
    print(f"EU Countries generic entry: {len(eu_generic):,} rows")
    print("Sectors for EU Countries:")
    print(eu_generic["Sector"].value_counts().to_string())
    print()
    print("Year distribution for EU Countries (last 10 years):")
    print(
        eu_generic["signature_date"]
        .dt.year.value_counts()
        .sort_index()
        .tail(10)
        .to_string()
    )


if __name__ == "__main__":
    main()
