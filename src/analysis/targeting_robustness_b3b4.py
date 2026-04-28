"""Targeting regression robustness checks B3 and B4.

B3: Euro area vs. non-euro area split — tests whether EIB targeting is
    concentrated in less financially integrated markets.
B4: High-constraint vs. low-constraint countries (median split) — tests
    whether targeting is non-linear (only responds above a threshold).

Both are exploratory heterogeneity analyses, not causal claims.
They help interpret the null targeting result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import pyfixest as pf

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def run_b3_euro_split():
    """B3: Euro area vs. non-euro area split."""
    print("\n=== B3: Euro area vs. non-euro area split ===")

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

    # Euro area membership as of 2015-2021 panel
    euro_countries = {
        "AT",
        "BE",
        "CY",
        "DE",
        "EE",
        "FI",
        "FR",
        "EL",
        "IE",
        "IT",
        "LT",
        "LU",
        "LV",
        "MT",
        "NL",
        "PT",
        "SI",
        "SK",
        "ES",
    }
    panel["is_euro"] = panel["country"].isin(euro_countries).astype(int)

    results = []

    def run_spec(data, label, notes=""):
        df = data.dropna(
            subset=["log_eib_per_sme", "access_to_finance_share", "log_gdp_pc"]
        )
        if len(df) < 20:
            print(f"  [SKIP] {label}: only {len(df)} obs")
            return

        print(f"\n--- {label} ---")
        print(f"  Observations: {len(df)}")
        print(f"  Countries: {df['country'].nunique()}")

        try:
            fit = pf.feols(
                "log_eib_per_sme ~ access_to_finance_share + log_gdp_pc | country + year",
                data=df,
                vcov={"CRV1": "country"},
            )
            print(fit.summary())
            coef = fit.coef().get("access_to_finance_share", np.nan)
            se = fit.se().get("access_to_finance_share", np.nan)
            tstat = fit.tstat().get("access_to_finance_share", np.nan)
            pval = fit.pvalue().get("access_to_finance_share", np.nan)
            r2 = getattr(fit, "_r2", np.nan)

            results.append(
                {
                    "check": "B3",
                    "spec": label,
                    "N": len(df),
                    "n_countries": df["country"].nunique(),
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
            results.append(
                {"check": "B3", "spec": label, "N": len(df), "notes": f"ERROR: {e}"}
            )

    euro = panel[panel["is_euro"] == 1]
    non_euro = panel[panel["is_euro"] == 0]

    run_spec(euro, "B3_euro_area", "Euro area countries only (financially integrated)")
    run_spec(
        non_euro, "B3_non_euro", "Non-euro countries only (less financially integrated)"
    )

    # Also test interaction: does the slope differ?
    print("\n--- B3_interaction (pooled with euro dummy interaction) ---")
    try:
        fit_int = pf.feols(
            "log_eib_per_sme ~ access_to_finance_share + access_to_finance_share:is_euro + log_gdp_pc | country + year",
            data=panel,
            vcov={"CRV1": "country"},
        )
        print(fit_int.summary())
        coef_int = fit_int.coef().get("access_to_finance_share:is_euro", np.nan)
        se_int = fit_int.se().get("access_to_finance_share:is_euro", np.nan)
        t_int = fit_int.tstat().get("access_to_finance_share:is_euro", np.nan)
        p_int = fit_int.pvalue().get("access_to_finance_share:is_euro", np.nan)

        results.append(
            {
                "check": "B3",
                "spec": "B3_interaction",
                "N": len(panel),
                "n_countries": panel["country"].nunique(),
                "beta_constraint": coef_int,
                "se_constraint": se_int,
                "t_stat": t_int,
                "p_value": p_int,
                "R2": getattr(fit_int, "_r2", np.nan),
                "notes": "Interaction: difference in targeting slope between euro and non-euro",
            }
        )
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(
            {
                "check": "B3",
                "spec": "B3_interaction",
                "N": len(panel),
                "notes": f"ERROR: {e}",
            }
        )

    return results


def run_b4_constraint_split():
    """B4: High-constraint vs. low-constraint countries (median split)."""
    print("\n=== B4: High-constraint vs. low-constraint countries ===")

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

    # Median split by constraint level (country-level mean constraint)
    country_mean_constraint = panel.groupby("country")["access_to_finance_share"].mean()
    median_constraint = country_mean_constraint.median()
    high_constraint_countries = set(
        country_mean_constraint[country_mean_constraint >= median_constraint].index
    )
    panel["is_high_constraint"] = (
        panel["country"].isin(high_constraint_countries).astype(int)
    )

    print(f"Median mean constraint: {median_constraint:.4f}")
    print(f"High-constraint countries: {sorted(high_constraint_countries)}")
    print(
        f"Low-constraint countries: {sorted(set(panel['country'].unique()) - high_constraint_countries)}"
    )

    results = []

    def run_spec(data, label, notes=""):
        df = data.dropna(
            subset=["log_eib_per_sme", "access_to_finance_share", "log_gdp_pc"]
        )
        if len(df) < 20:
            print(f"  [SKIP] {label}: only {len(df)} obs")
            return

        print(f"\n--- {label} ---")
        print(f"  Observations: {len(df)}")
        print(f"  Countries: {df['country'].nunique()}")

        try:
            fit = pf.feols(
                "log_eib_per_sme ~ access_to_finance_share + log_gdp_pc | country + year",
                data=df,
                vcov={"CRV1": "country"},
            )
            print(fit.summary())
            coef = fit.coef().get("access_to_finance_share", np.nan)
            se = fit.se().get("access_to_finance_share", np.nan)
            tstat = fit.tstat().get("access_to_finance_share", np.nan)
            pval = fit.pvalue().get("access_to_finance_share", np.nan)
            r2 = getattr(fit, "_r2", np.nan)

            results.append(
                {
                    "check": "B4",
                    "spec": label,
                    "N": len(df),
                    "n_countries": df["country"].nunique(),
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
            results.append(
                {"check": "B4", "spec": label, "N": len(df), "notes": f"ERROR: {e}"}
            )

    high = panel[panel["is_high_constraint"] == 1]
    low = panel[panel["is_high_constraint"] == 0]

    run_spec(
        high,
        "B4_high_constraint",
        f"High-constraint countries (mean >= {median_constraint:.4f})",
    )
    run_spec(
        low,
        "B4_low_constraint",
        f"Low-constraint countries (mean < {median_constraint:.4f})",
    )

    # Interaction: does slope differ by constraint level?
    print("\n--- B4_interaction (pooled with high-constraint dummy interaction) ---")
    try:
        fit_int = pf.feols(
            "log_eib_per_sme ~ access_to_finance_share + access_to_finance_share:is_high_constraint + log_gdp_pc | country + year",
            data=panel,
            vcov={"CRV1": "country"},
        )
        print(fit_int.summary())
        coef_int = fit_int.coef().get(
            "access_to_finance_share:is_high_constraint", np.nan
        )
        se_int = fit_int.se().get("access_to_finance_share:is_high_constraint", np.nan)
        t_int = fit_int.tstat().get(
            "access_to_finance_share:is_high_constraint", np.nan
        )
        p_int = fit_int.pvalue().get(
            "access_to_finance_share:is_high_constraint", np.nan
        )

        results.append(
            {
                "check": "B4",
                "spec": "B4_interaction",
                "N": len(panel),
                "n_countries": panel["country"].nunique(),
                "beta_constraint": coef_int,
                "se_constraint": se_int,
                "t_stat": t_int,
                "p_value": p_int,
                "R2": getattr(fit_int, "_r2", np.nan),
                "notes": "Interaction: difference in targeting slope between high and low constraint countries",
            }
        )
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(
            {
                "check": "B4",
                "spec": "B4_interaction",
                "N": len(panel),
                "notes": f"ERROR: {e}",
            }
        )

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("TARGETING REGRESSION ROBUSTNESS CHECKS — B3 and B4")
    print("=" * 70)

    b3_results = run_b3_euro_split()
    b4_results = run_b4_constraint_split()

    all_results = b3_results + b4_results
    results_df = pd.DataFrame(all_results)

    # Append to existing robustness table
    existing = OUTPUTS_TABLES / "phase1_targeting_robustness.csv"
    if existing.exists():
        old = pd.read_csv(existing)
        combined = pd.concat([old, results_df], ignore_index=True)
    else:
        combined = results_df

    out = OUTPUTS_TABLES / "phase1_targeting_robustness.csv"
    combined.to_csv(out, index=False)
    print(f"\n{'='*70}")
    print(f"Saved combined results to {out}")
    print(f"{'='*70}")
    print(combined.to_string())
