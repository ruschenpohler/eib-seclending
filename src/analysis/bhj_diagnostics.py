"""Borusyak-Hull-Jaravel (2022) shift-share validity diagnostics.

Computes:
1. Effective number of shocks (inverse Herfindahl of average employment shares)
2. Share concentration by country
3. Shock variance summary

These diagnostics make explicit the identifying variation in the Bartik
instrument before the first-stage F-statistic is even computed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from src.config import DATA_RAW, OUTPUTS_TABLES


def compute_bhj_diagnostics():
    """Compute BHJ equivalent sample size and shock concentration."""
    print("=" * 60)
    print("BHJ SHIFT-SHARE DIAGNOSTICS")
    print("=" * 60)

    # Load employment shares (base year 2015)
    sbs = pd.read_csv(DATA_RAW / "eurostat_sbs_sc_sca_r2.csv")
    sbs = sbs[sbs["indic_sb"] == "V16110"]
    sbs = sbs[sbs["time_period"] == 2015]
    emp = (
        sbs.groupby(["geo", "nace_r2"])["value"]
        .sum()
        .reset_index()
        .rename(
            columns={"geo": "country", "nace_r2": "nace_section", "value": "employment"}
        )
    )
    total = (
        emp.groupby("country")["employment"]
        .sum()
        .reset_index()
        .rename(columns={"employment": "total_employment"})
    )
    emp = emp.merge(total, on="country", how="left")
    emp["employment_share"] = emp["employment"] / emp["total_employment"]

    # Average share across countries
    avg_shares = emp.groupby("nace_section")["employment_share"].mean().reset_index()
    avg_shares = avg_shares.rename(columns={"employment_share": "avg_share"})

    # Effective number of shocks: inverse Herfindahl
    n_eff = 1.0 / (avg_shares["avg_share"] ** 2).sum()

    print(f"\nNominal number of shocks (NACE sections): {len(avg_shares)}")
    print(f"Effective number of shocks (inverse Herfindahl): {n_eff:.2f}")
    print("\nAverage employment shares by sector:")
    print(avg_shares.sort_values("avg_share", ascending=False).to_string(index=False))

    # Herfindahl by country
    emp = emp.merge(avg_shares, on="nace_section", how="left")
    country_hhi = (
        emp.groupby("country")
        .apply(lambda x: (x["employment_share"] ** 2).sum())
        .reset_index()
        .rename(columns={0: "hhi"})
    )
    country_hhi["n_eff_country"] = 1.0 / country_hhi["hhi"]

    print("\nEffective shocks by country (inverse HHI):")
    print(country_hhi.sort_values("n_eff_country").to_string(index=False))

    # Save
    diag = {
        "nominal_shocks": len(avg_shares),
        "effective_shocks": n_eff,
        "mean_hhi": country_hhi["hhi"].mean(),
        "median_n_eff_country": country_hhi["n_eff_country"].median(),
    }
    diag_df = pd.DataFrame([diag])
    out = OUTPUTS_TABLES / "phase2b_bhj_diagnostics.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    diag_df.to_csv(out, index=False)
    print(f"\nSaved diagnostics to {out}")

    return diag


if __name__ == "__main__":
    compute_bhj_diagnostics()
