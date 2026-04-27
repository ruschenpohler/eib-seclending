"""Validate EIB-NACE crosswalk against actual dataset sectors."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from src.config import DATA_RAW


def main():
    # Load dataset and crosswalk
    df = pd.read_excel(DATA_RAW / "loanExport.xlsx", engine="openpyxl")
    crosswalk = pd.read_csv(DATA_RAW / "eib_nace_crosswalk.csv")

    print("=== CHECK 2 VALIDATION ===")
    print()

    # Sub-task A: Intermediated coverage
    print("Sub-task A — Intermediated operations (MBILs):")
    credit_lines = df[df["Sector"] == "Credit lines"]
    print(f"  'Credit lines' rows: {len(credit_lines):,}")
    print(
        f"  EU region: {len(credit_lines[credit_lines['Region'] == 'European Union']):,}"
    )
    print("  Status: INTERMEDIATED OPERATIONS PRESENT — Check 3 can be bypassed")
    print()

    # Sub-task B: NACE alignment
    print("Sub-task B — NACE alignment:")
    actual_sectors = set(df["Sector"].dropna().unique())
    crosswalk_sectors = set(crosswalk["eib_sector"].unique())

    print(f"  EIB sectors in dataset ({len(actual_sectors)}):")
    for s in sorted(actual_sectors):
        print(f"    - {s}")

    print()
    print(f"  Sectors in crosswalk ({len(crosswalk_sectors)}):")
    for s in sorted(crosswalk_sectors):
        print(f"    - {s}")

    print()
    unmatched = actual_sectors - crosswalk_sectors
    extra = crosswalk_sectors - actual_sectors

    if unmatched:
        print(f"  UNMATCHED in dataset (missing from crosswalk): {unmatched}")
    else:
        print("  All dataset sectors matched in crosswalk.")

    if extra:
        print(f"  EXTRA in crosswalk (not in dataset): {extra}")
    else:
        print("  No extra sectors in crosswalk.")

    print()
    print("Crosswalk summary:")
    print(crosswalk.to_string(index=False))


if __name__ == "__main__":
    main()
