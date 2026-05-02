"""Robustness checks on the between-country targeting estimator.

Three variations:
1. Drop small countries (LU, MT, CY, SI)
2. Single cross-section (2019 only)
3. Median instead of mean

All use HC3 standard errors.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def run_between_robustness():
    """Run three robustness variations of the between estimator."""
    print("=" * 60)
    print("BETWEEN ESTIMATOR ROBUSTNESS CHECKS")
    print("=" * 60)

    panel = pd.read_csv(DATA_PROCESSED / "eib_analysis_panel.csv")
    panel = panel.dropna(
        subset=["eib_per_sme", "access_to_finance_share", "gdp_per_capita", "country"]
    )

    results = []

    def run_spec(data, label, notes=""):
        """Run one between specification and append to results."""
        if len(data) < 10:
            print(f"  [SKIP] {label}: only {len(data)} obs")
            return

        X = sm.add_constant(data[["constraint_mean", "log_gdp_pc"]])
        y = data["log_eib_per_sme"]
        model = sm.OLS(y, X)
        fit = model.fit(cov_type="HC3")

        coef = fit.params["constraint_mean"]
        se = fit.bse["constraint_mean"]
        pval = fit.pvalues["constraint_mean"]
        ci = fit.conf_int().loc["constraint_mean"]

        print(f"\n--- {label} ---")
        print(f"  N = {len(data)}")
        print(f"  beta = {coef:+.3f}, SE = {se:.3f}")
        print(f"  95% CI = [{ci[0]:.2f}, {ci[1]:.2f}]")
        print(f"  p = {pval:.4f}")

        results.append(
            {
                "spec": label,
                "N": len(data),
                "beta_constraint": coef,
                "se_constraint": se,
                "ci_lower": ci[0],
                "ci_upper": ci[1],
                "p_value": pval,
                "R2": fit.rsquared,
                "notes": notes,
            }
        )

    # Baseline (for comparison)
    country_means = (
        panel.groupby("country")
        .agg(
            constraint_mean=("access_to_finance_share", "mean"),
            eib_per_sme_mean=("eib_per_sme", "mean"),
            gdp_pc_mean=("gdp_per_capita", "mean"),
        )
        .reset_index()
    )
    country_means["log_eib_per_sme"] = np.log(country_means["eib_per_sme_mean"])
    country_means["log_gdp_pc"] = np.log(country_means["gdp_pc_mean"])

    run_spec(country_means, "Baseline (mean, all countries)", "Baseline for comparison")

    # i. Drop small countries
    small = {"LU", "MT", "CY", "SI"}
    country_means_no_small = country_means[~country_means["country"].isin(small)]
    run_spec(
        country_means_no_small,
        "Drop small countries (LU, MT, CY, SI)",
        "Excludes countries with extreme per-SME volatility",
    )

    # ii. Single cross-section (2019)
    panel_2019 = panel[panel["year"] == 2019].copy()
    if len(panel_2019) > 0:
        cs_2019 = (
            panel_2019.groupby("country")
            .agg(
                constraint_mean=("access_to_finance_share", "mean"),
                eib_per_sme_mean=("eib_per_sme", "mean"),
                gdp_pc_mean=("gdp_per_capita", "mean"),
            )
            .reset_index()
        )
        cs_2019["log_eib_per_sme"] = np.log(cs_2019["eib_per_sme_mean"])
        cs_2019["log_gdp_pc"] = np.log(cs_2019["gdp_pc_mean"])
        run_spec(
            cs_2019,
            "Single year (2019)",
            "Pre-COVID cross-section, no time averaging",
        )

    # iii. Median instead of mean
    country_medians = (
        panel.groupby("country")
        .agg(
            constraint_mean=("access_to_finance_share", "median"),
            eib_per_sme_mean=("eib_per_sme", "median"),
            gdp_pc_mean=("gdp_per_capita", "median"),
        )
        .reset_index()
    )
    country_medians["log_eib_per_sme"] = np.log(country_medians["eib_per_sme_mean"])
    country_medians["log_gdp_pc"] = np.log(country_medians["gdp_pc_mean"])
    run_spec(
        country_medians,
        "Median (instead of mean)",
        "Robust to within-country outlier years",
    )

    # Save
    df = pd.DataFrame(results)
    out = OUTPUTS_TABLES / "phase1_targeting_between_robustness.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nSaved to {out}")
    print(df.to_string(index=False))

    return df


if __name__ == "__main__":
    run_between_robustness()
