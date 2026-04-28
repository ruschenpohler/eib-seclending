"""Targeting regression robustness checks A1, B1, B2, C1.

A1: Q0b mean importance score (intensity vs. ranking)
B1: Exclude 2020 (COVID)
B2: High-income vs. low-income subsamples
C1: EIB-relevant sectors as denominator

All specs use the same base model:
    log(EIB_per_SME) = β·constraint + γ·log(GDP_pc) + country_FE + year_FE + ε
    SEs clustered at country level.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import pyfixest as pf

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def run_all_robustness():
    print("=== Targeting Regression Robustness Checks ===\n")

    # Load panel
    panel = pd.read_csv(DATA_PROCESSED / "eib_analysis_panel.csv")
    panel = panel.dropna(
        subset=[
            "eib_per_sme",
            "access_to_finance_share",
            "gdp_per_capita",
            "country",
            "year",
        ]
    )
    panel["log_eib_per_sme"] = np.log(panel["eib_per_sme"])
    panel["log_gdp_pc"] = np.log(panel["gdp_per_capita"])
    panel["country_code"] = panel["country"].astype("category")
    panel["year_code"] = panel["year"].astype("category")

    results = []

    def run_spec(data, constraint_var, label, notes=""):
        """Run one specification and append to results."""
        df = data.dropna(subset=["log_eib_per_sme", constraint_var, "log_gdp_pc"])
        if len(df) < 30:
            print(f"  [SKIP] {label}: only {len(df)} obs")
            return

        print(f"\n--- {label} ---")
        print(f"  Observations: {len(df)}")

        try:
            fit = pf.feols(
                f"log_eib_per_sme ~ {constraint_var} + log_gdp_pc | country_code + year_code",
                data=df,
                vcov={"CRV1": "country_code"},
            )
            print(fit.summary())
            coef = fit.coef().get(constraint_var, np.nan)
            se = fit.se().get(constraint_var, np.nan)
            tstat = fit.tstat().get(constraint_var, np.nan)
            pval = fit.pvalue().get(constraint_var, np.nan)
            r2 = getattr(fit, "_r2", np.nan)

            results.append(
                {
                    "spec": label,
                    "N": len(df),
                    "beta_constraint": coef,
                    "se_constraint": se,
                    "t_stat": tstat,
                    "p_value": pval,
                    "R2": r2,
                    "notes": notes,
                }
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"spec": label, "N": len(df), "notes": f"ERROR: {e}"})

    # Baseline (for comparison)
    run_spec(
        panel,
        "access_to_finance_share",
        "baseline_spec_1a",
        "Replicated for comparison",
    )

    # A1: Q0b mean importance score
    q0b = pd.read_csv(DATA_PROCESSED.parent / "interim" / "safe_q0b_panel.csv")
    panel_a1 = panel.merge(q0b, on=["country", "year"], how="left")
    run_spec(
        panel_a1,
        "access_to_finance_mean_score",
        "A1_q0b_mean_score",
        "Intensity measure: mean 1-10 score instead of share ranking as most important problem",
    )

    # B1: Exclude 2020
    panel_b1 = panel[panel["year"] != 2020]
    run_spec(
        panel_b1,
        "access_to_finance_share",
        "B1_exclude_2020",
        "COVID year excluded to test whether null is driven by pandemic disruption",
    )

    # B2: Subsample splits
    median_gdp = panel["gdp_per_capita"].median()
    panel_b2_high = panel[panel["gdp_per_capita"] >= median_gdp]
    panel_b2_low = panel[panel["gdp_per_capita"] < median_gdp]
    run_spec(
        panel_b2_high,
        "access_to_finance_share",
        "B2_high_income",
        f"High-income subsample (GDP/capita >= {median_gdp:,.0f})",
    )
    run_spec(
        panel_b2_low,
        "access_to_finance_share",
        "B2_low_income",
        f"Low-income subsample (GDP/capita < {median_gdp:,.0f})",
    )

    # C1: EIB-relevant sectors denominator
    # EIB-relevant NACE sections from our crosswalk: C, D, E, F, G, H, I, J, L, M, N
    # Recalculate eib_per_sme using only these sectors
    sbs = pd.read_csv(DATA_PROCESSED.parent / "raw" / "eurostat_sbs_sc_sca_r2.csv")
    sbs["time_period"] = sbs["time_period"].astype(int)
    eib_nace = {"C", "D", "E", "F", "G", "H", "I", "J", "L", "M", "N"}
    sbs_eib = sbs[(sbs["nace_r2"].isin(eib_nace)) & (sbs["indic_sb"] == "V11110")]
    sme_eib = (
        sbs_eib.groupby(["geo", "time_period"])["value"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "geo": "country",
                "time_period": "year",
                "value": "sme_enterprises_eib",
            }
        )
    )
    panel_c1 = panel.merge(sme_eib, on=["country", "year"], how="left")
    panel_c1["eib_per_sme_eib"] = (
        panel_c1["eib_signed_amount"] / panel_c1["sme_enterprises_eib"]
    )
    panel_c1["log_eib_per_sme_eib"] = np.log(panel_c1["eib_per_sme_eib"])
    # Replace the LHS variable for this spec
    panel_c1["log_eib_per_sme"] = panel_c1["log_eib_per_sme_eib"]
    run_spec(
        panel_c1,
        "access_to_finance_share",
        "C1_eib_sectors_denominator",
        "Denominator = SME enterprises in EIB-relevant NACE sections only (C,D,E,F,G,H,I,J,L,M,N)",
    )

    # Save
    results_df = pd.DataFrame(results)
    out = OUTPUTS_TABLES / "phase1_targeting_robustness.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out, index=False)
    print(f"\n{'='*60}")
    print(f"Saved results to {out}")
    print(f"{'='*60}")
    print(results_df.to_string())

    return results_df


if __name__ == "__main__":
    run_all_robustness()
