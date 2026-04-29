"""Cohesion eligibility data loader and validator (Check 6).

Expected input: data/raw/cohesion_eligibility.csv
Schema: nuts2_code, nuts2_name, country, period, category
where category ∈ {less_developed, transition, more_developed}
period ∈ {2007-2013, 2014-2020, 2021-2027}

Outputs:
- Validation report (country coverage, category counts, reclassifications)
- Summary table for README / descriptive section
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from src.config import DATA_RAW, OUTPUTS_TABLES


def validate_cohesion_data(filepath: Path) -> dict:
    """Load and validate cohesion eligibility CSV.

    Returns:
        dict with validation results and summary statistics.
    """
    if not filepath.exists():
        return {"valid": False, "error": f"File not found: {filepath}"}

    df = pd.read_csv(filepath)

    # Schema check
    required_cols = {"nuts2_code", "nuts2_name", "country", "period", "category"}
    missing = required_cols - set(df.columns)
    if missing:
        return {
            "valid": False,
            "error": f"Missing columns: {missing}",
            "columns": list(df.columns),
        }

    # Category check
    valid_cats = {"less_developed", "transition", "more_developed"}
    invalid_cats = set(df["category"].unique()) - valid_cats
    if invalid_cats:
        print(f"Warning: unexpected categories found: {invalid_cats}")

    # Period check
    valid_periods = {"2007-2013", "2014-2020", "2021-2027"}
    invalid_periods = set(df["period"].unique()) - valid_periods
    if invalid_periods:
        print(f"Warning: unexpected periods found: {invalid_periods}")

    # Summary stats
    n_regions = df["nuts2_code"].nunique()
    n_countries = df["country"].nunique()
    period_counts = df.groupby("period").size().to_dict()
    category_counts = df.groupby(["period", "category"]).size().unstack(fill_value=0)

    # Reclassification events: regions that change category across periods
    if len(df["period"].unique()) >= 2:
        wide = df.pivot(index="nuts2_code", columns="period", values="category")
        reclass = 0
        reclass_details = []
        for p1, p2 in [("2007-2013", "2014-2020"), ("2014-2020", "2021-2027")]:
            if p1 in wide.columns and p2 in wide.columns:
                changed = wide[wide[p1] != wide[p2]].dropna(subset=[p1, p2])
                reclass += len(changed)
                for nuts2, row in changed.iterrows():
                    reclass_details.append(
                        {
                            "nuts2_code": nuts2,
                            "from_period": p1,
                            "to_period": p2,
                            "from_cat": row[p1],
                            "to_cat": row[p2],
                        }
                    )
    else:
        reclass = 0
        reclass_details = []

    results = {
        "valid": True,
        "n_rows": len(df),
        "n_regions": n_regions,
        "n_countries": n_countries,
        "period_counts": period_counts,
        "category_counts": category_counts.to_dict(),
        "reclassification_count": reclass,
        "reclassification_details": reclass_details,
        "check_6_pass": reclass >= 15,
    }

    return results


def print_validation(results: dict):
    """Print validation report to stdout."""
    if not results["valid"]:
        print(f"VALIDATION FAILED: {results['error']}")
        return

    print("=" * 60)
    print("COHESION ELIGIBILITY DATA VALIDATION")
    print("=" * 60)
    print(f"Total rows: {results['n_rows']}")
    print(f"Unique NUTS-2 regions: {results['n_regions']}")
    print(f"Countries covered: {results['n_countries']}")
    print("\nPeriod coverage:")
    for period, count in results["period_counts"].items():
        print(f"  {period}: {count} regions")
    print(
        f"\nReclassification events (category changes across periods): {results['reclassification_count']}"
    )
    print(
        f"Check 6 pass criterion (≥15): {'PASS' if results['check_6_pass'] else 'FAIL'}"
    )

    if results["reclassification_details"]:
        print("\nReclassification details (first 10):")
        for r in results["reclassification_details"][:10]:
            print(
                f"  {r['nuts2_code']}: {r['from_cat']} ({r['from_period']}) → {r['to_cat']} ({r['to_period']})"
            )

    # Save summary
    summary = pd.DataFrame(results["category_counts"])
    out = OUTPUTS_TABLES / "phase1_cohesion_summary.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out)
    print(f"\nSaved summary to {out}")


if __name__ == "__main__":
    filepath = DATA_RAW / "cohesion_eligibility.csv"
    results = validate_cohesion_data(filepath)
    print_validation(results)
