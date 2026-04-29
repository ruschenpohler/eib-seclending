"""Reconstruct cohesion eligibility from Eurostat NUTS-2 GDP (PPS) data.

Fetches nama_10r_2gdp with unit=PPS_EU27_2020_HAB, computes 3-year average
GDP/capita in PPS for each reference period, classifies regions relative to
EU-27 average:
    - Less Developed: < 75%
    - Transition: 75-90%
    - More Developed: > 90%

Notes:
- This is a reconstruction, not the official DG REGIO list. Minor deviations
  expected due to political exceptions (islands, border regions).
- Uses latest NUTS vintage with back-casting; official lists use period-specific
  vintages (NUTS 2006, 2010, 2016).
- Values are absolute PPS per capita, not indices. EU-27 average computed
  from the same dataset.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import requests

from src.config import DATA_RAW, OUTPUTS_TABLES


def fetch_eurostat_gdp_pps():
    """Fetch NUTS-2 GDP per capita in PPS from Eurostat JSON API."""
    print("Fetching NUTS-2 GDP (PPS per capita) from Eurostat...")
    base = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    params = {"format": "JSON", "lang": "EN", "unit": "PPS_EU27_2020_HAB"}
    r = requests.get(base + "nama_10r_2gdp", params=params, timeout=120)
    r.raise_for_status()
    data = r.json()

    # Parse sparse value dict
    value_dict = data["value"]
    dims = data["dimension"]
    dim_ids = data["id"]
    indices = {d: list(dims[d]["category"]["index"].keys()) for d in dim_ids}
    sizes = [len(indices[d]) for d in dim_ids]

    records = []
    for idx_str, val in value_dict.items():
        idx = int(idx_str)
        coords = {}
        rem = idx
        for d, size in zip(dim_ids, sizes):
            coords[d] = indices[d][rem % size]
            rem //= size
        coords["value"] = val
        records.append(coords)

    df = pd.DataFrame(records)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.rename(columns={"time": "year"})
    df["year"] = df["year"].astype(int)
    print(f"  Retrieved {len(df)} rows")
    return df


def assign_cohesion_categories(df_gdp):
    """Assign cohesion categories based on 3-year average GDP/capita PPS."""
    # Filter to NUTS-2 (4-character geo codes)
    df = df_gdp[df_gdp["geo"].str.len() == 4].copy()

    # EU-27 country prefixes
    eu27 = [
        "AT",
        "BE",
        "BG",
        "CY",
        "CZ",
        "DE",
        "DK",
        "EE",
        "EL",
        "ES",
        "FI",
        "FR",
        "HR",
        "HU",
        "IE",
        "IT",
        "LT",
        "LU",
        "LV",
        "MT",
        "NL",
        "PL",
        "PT",
        "RO",
        "SE",
        "SI",
        "SK",
    ]
    df = df[df["geo"].str[:2].isin(eu27)]

    # Compute EU-27 average by year (simple mean across NUTS-2 regions)
    eu_avg = df.groupby("year")["value"].mean().reset_index()
    eu_avg = eu_avg.rename(columns={"value": "eu_avg_pps"})

    # Merge and compute % of EU average
    df = df.merge(eu_avg, on="year", how="left")
    df["pct_of_eu_avg"] = 100 * df["value"] / df["eu_avg_pps"]

    # Reference periods
    periods = {
        "2007-2013": [2004, 2005, 2006],
        "2014-2020": [2007, 2008, 2009],
        "2021-2027": [2015, 2016, 2017],
    }

    results = []
    for period_name, years in periods.items():
        dp = df[df["year"].isin(years)].copy()
        # Average across reference years
        avg = (
            dp.groupby("geo")
            .agg(
                avg_gdp_pps=("value", "mean"),
                avg_pct_of_eu=("pct_of_eu_avg", "mean"),
                n_years=("year", "count"),
            )
            .reset_index()
        )
        avg = avg[avg["n_years"] >= 2]  # Require at least 2 years
        avg["period"] = period_name
        avg["category"] = pd.cut(
            avg["avg_pct_of_eu"],
            bins=[0, 75, 90, float("inf")],
            labels=["less_developed", "transition", "more_developed"],
        )
        avg["country"] = avg["geo"].str[:2]
        results.append(avg)

    return pd.concat(results, ignore_index=True)


def save_and_summarize(df):
    """Save CSV and print summary."""
    # Add region names (best effort — use geo code as name)
    df["nuts2_name"] = df["geo"]
    out = df[
        [
            "geo",
            "nuts2_name",
            "country",
            "period",
            "category",
            "avg_gdp_pps",
            "avg_pct_of_eu",
            "n_years",
        ]
    ]
    out = out.rename(columns={"geo": "nuts2_code"})

    filepath = DATA_RAW / "cohesion_eligibility.csv"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(filepath, index=False)
    print(f"\nSaved to {filepath}")

    # Summary
    print("\n" + "=" * 60)
    print("COHESION ELIGIBILITY RECONSTRUCTION SUMMARY")
    print("=" * 60)
    print(f"Total rows: {len(out)}")
    print(f"Unique NUTS-2 regions: {out['nuts2_code'].nunique()}")
    print(f"Countries: {out['country'].nunique()}")
    print("\nPeriod coverage:")
    print(out.groupby("period").size())
    print("\nCategory distribution by period:")
    print(out.groupby(["period", "category"]).size().unstack(fill_value=0))

    # Reclassifications
    if out["period"].nunique() >= 2:
        wide = out.pivot(index="nuts2_code", columns="period", values="category")
        reclass = 0
        for p1, p2 in [("2007-2013", "2014-2020"), ("2014-2020", "2021-2027")]:
            if p1 in wide.columns and p2 in wide.columns:
                changed = wide[wide[p1] != wide[p2]].dropna(subset=[p1, p2])
                reclass += len(changed)
                if len(changed) > 0:
                    print(f"\nReclassifications {p1} -> {p2}: {len(changed)}")
                    print(changed.head())
        print(f"\nTotal reclassification events: {reclass}")
        print(f"Check 6 pass (>=15): {'PASS' if reclass >= 15 else 'FAIL'}")

    # Save summary table
    summary = out.groupby(["period", "category"]).size().unstack(fill_value=0)
    summary_path = OUTPUTS_TABLES / "phase1_cohesion_summary.csv"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path)
    print(f"\nSaved summary to {summary_path}")

    return out


if __name__ == "__main__":
    print("=" * 60)
    print("COHESION ELIGIBILITY RECONSTRUCTION")
    print("=" * 60)
    gdp = fetch_eurostat_gdp_pps()
    cohesion = assign_cohesion_categories(gdp)
    save_and_summarize(cohesion)
    print("\nDone. Run src/ingest/cohesion.py to validate.")
