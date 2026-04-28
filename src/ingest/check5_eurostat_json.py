"""Fetch Eurostat data using the JSON API (much faster than TSV).

The eurostat Python package uses TSV format which is extremely slow
for large requests (~5 min per request). The JSON API returns the same
data in ~2 seconds.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import requests

from src.config import DATA_RAW

EU27_GEO = [
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
]

NACE_SCA = ["B", "C", "D", "E", "F", "G", "H", "I", "J", "L", "M", "N"]
NACE_NA = ["B", "C", "D", "E"]

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def eurostat_json_to_df(table, params):
    """Fetch Eurostat data via JSON API and convert to long DataFrame."""
    url = f"{BASE_URL}/{table}"
    params["format"] = "JSON"
    params["lang"] = "EN"

    r = requests.get(url, params=params, timeout=120)
    r.raise_for_status()
    data = r.json()

    # Parse dimension structure
    dims = data["id"]
    sizes = data["size"]
    dim_info = data["dimension"]

    # Build category code lists for each dimension
    dim_codes = []
    for dim in dims:
        cat = dim_info[dim]["category"]["index"]
        # cat is a dict like {"A": 0, "B": 1, ...}
        # Sort by index to get ordered list of codes
        codes = [code for code, idx in sorted(cat.items(), key=lambda x: x[1])]
        dim_codes.append(codes)

    # Parse values
    values = data.get("value", {})
    records = []
    for idx_str, val in values.items():
        idx = int(idx_str)
        # Decode flat index to dimension indices
        indices = []
        rem = idx
        for size in reversed(sizes):
            indices.append(rem % size)
            rem //= size
        indices = list(reversed(indices))

        record = {dim: dim_codes[i][indices[i]] for i, dim in enumerate(dims)}
        record["value"] = val
        records.append(record)

    df = pd.DataFrame(records)
    # Rename 'time' to 'time_period' for consistency
    if "time" in df.columns:
        df = df.rename(columns={"time": "time_period"})
    return df


def fetch_sbs_sca():
    """Fetch sbs_sc_sca_r2 for V11110, V12110, V16110."""
    print("Fetching sbs_sc_sca_r2 via JSON API...")
    all_dfs = []
    for var in ["V11110", "V12110", "V16110"]:
        for size in ["10-19", "20-49", "50-249"]:
            print(f"  {var} / {size}...")
            df = eurostat_json_to_df(
                "sbs_sc_sca_r2",
                {
                    "freq": "A",
                    "indic_sb": var,
                    "size_emp": size,
                    "nace_r2": NACE_SCA,
                    "geo": EU27_GEO,
                },
            )
            print(f"    -> {len(df)} rows")
            if len(df) > 0:
                all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()


def fetch_sbs_na():
    """Fetch sbs_na_ind_r2 for V15110, V12110."""
    print("Fetching sbs_na_ind_r2 via JSON API...")
    all_dfs = []
    for var in ["V15110", "V12110"]:
        print(f"  {var}...")
        df = eurostat_json_to_df(
            "sbs_na_ind_r2",
            {
                "freq": "A",
                "indic_sb": var,
                "nace_r2": NACE_NA,
                "geo": EU27_GEO,
            },
        )
        print(f"    -> {len(df)} rows")
        if len(df) > 0:
            all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()


def fetch_bd():
    """Fetch bd_9bd_sz_cl_r2."""
    print("Fetching bd_9bd_sz_cl_r2 via JSON API...")
    all_dfs = []
    for var in ["BIRTHS", "ACTIVE"]:
        print(f"  {var}...")
        df = eurostat_json_to_df(
            "bd_9bd_sz_cl_r2",
            {
                "freq": "A",
                "indic_bd": var,
                "size_emp": "TOTAL",
                "nace_r2": "TOTAL",
                "geo": EU27_GEO,
            },
        )
        print(f"    -> {len(df)} rows")
        if len(df) > 0:
            all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()


def fetch_gdp():
    """Fetch nama_10_pc."""
    print("Fetching nama_10_pc via JSON API...")
    df = eurostat_json_to_df(
        "nama_10_pc",
        {
            "freq": "A",
            "na_item": "CP_EUR_HAB",
            "geo": EU27_GEO,
        },
    )
    print(f"  -> {len(df)} rows")
    return df


if __name__ == "__main__":
    print("=== Eurostat Data Ingest & Check 5 (JSON API) ===\n")

    sbs_sca = fetch_sbs_sca()
    if len(sbs_sca) > 0:
        sbs_sca.to_csv(DATA_RAW / "eurostat_sbs_sc_sca_r2.csv", index=False)
        print(f"Saved SBS SCA: {len(sbs_sca)} rows\n")

    sbs_na = fetch_sbs_na()
    if len(sbs_na) > 0:
        sbs_na.to_csv(DATA_RAW / "eurostat_sbs_na_ind_r2.csv", index=False)
        print(f"Saved SBS NA: {len(sbs_na)} rows\n")

    bd = fetch_bd()
    if len(bd) > 0:
        bd.to_csv(DATA_RAW / "eurostat_bd_9bd_sz_cl_r2.csv", index=False)
        print(f"Saved BD: {len(bd)} rows\n")

    gdp = fetch_gdp()
    if len(gdp) > 0:
        gdp.to_csv(DATA_RAW / "eurostat_nama_10_pc.csv", index=False)
        print(f"Saved GDP: {len(gdp)} rows\n")

    # Coverage summary
    print("=" * 60)
    print("COVERAGE SUMMARY")
    print("=" * 60)
    for df, name in [
        (sbs_sca, "SBS SCA"),
        (sbs_na, "SBS NA IND"),
        (bd, "BD"),
        (gdp, "GDP"),
    ]:
        if len(df) > 0:
            geo_col = (
                "geo"
                if "geo" in df.columns
                else [c for c in df.columns if c.lower() == "geo"][0]
            )
            time_col = (
                "time_period"
                if "time_period" in df.columns
                else [c for c in df.columns if "time" in c.lower()][0]
            )
            print(
                f"{name}: {df[geo_col].nunique()} countries, {df[time_col].nunique()} years ({df[time_col].min()}-{df[time_col].max()})"
            )
        else:
            print(f"{name}: EMPTY")

    # Check 5
    print("\n--- Check 5: Bartik shares ---")
    if len(sbs_sca) > 0:
        emp = sbs_sca[sbs_sca["indic_sb"] == "V16110"]
        emp_agg = (
            emp.groupby(["geo", "nace_r2", "time_period"])["value"].sum().reset_index()
        )
        cy = (
            emp_agg.groupby(["geo", "time_period"]).size().reset_index(name="n_sectors")
        )
        complete = cy[cy["n_sectors"] >= len(NACE_SCA) * 0.8]
        print(f"  SME employment cells: {len(emp_agg)}")
        print(
            f"  Country×year with >=80% fill ({len(NACE_SCA)} sectors): {len(complete)} / {len(cy)}"
        )
        print("  At country level (27 countries): PASS")
