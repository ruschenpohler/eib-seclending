"""Between-country targeting estimator.

Collapses the panel to country means and estimates whether countries with
worse average financing constraints receive more average EIB lending per SME.
This is a cross-sectional, between-country test of structural targeting,
distinct from the within-country, time-varying test in the main specification.

Uses HC3 heteroskedasticity-robust standard errors (small sample, N=27).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def run_between_estimator():
    """Run between-country targeting estimator on collapsed panel."""
    print("=" * 60)
    print("BETWEEN-COUNTRY TARGETING ESTIMATOR")
    print("=" * 60)

    panel = pd.read_csv(DATA_PROCESSED / "eib_analysis_panel.csv")
    panel = panel.dropna(
        subset=["eib_per_sme", "access_to_finance_share", "gdp_per_capita", "country"]
    )

    # Collapse to country means (2015-2021)
    country_means = (
        panel.groupby("country")
        .agg(
            eib_per_sme_mean=("eib_per_sme", "mean"),
            constraint_mean=("access_to_finance_share", "mean"),
            gdp_pc_mean=("gdp_per_capita", "mean"),
            n_years=("year", "count"),
        )
        .reset_index()
    )

    print(f"Countries: {len(country_means)}")
    print(
        f"Years per country: {country_means['n_years'].min()}-{country_means['n_years'].max()}"
    )

    # Log transforms
    country_means["log_eib_per_sme"] = np.log(country_means["eib_per_sme_mean"])
    country_means["log_gdp_pc"] = np.log(country_means["gdp_pc_mean"])

    # OLS with HC3 SEs
    print("\n--- Between estimator: log(EIB/SME) ~ constraint + log(GDP) ---")
    model = smf.ols(
        "log_eib_per_sme ~ constraint_mean + log_gdp_pc",
        data=country_means,
    )
    fit = model.fit(cov_type="HC3")
    print(fit.summary())

    coef = fit.params["constraint_mean"]
    se = fit.bse["constraint_mean"]
    tstat = fit.tvalues["constraint_mean"]
    pval = fit.pvalues["constraint_mean"]
    ci_lower = fit.conf_int().loc["constraint_mean", 0]
    ci_upper = fit.conf_int().loc["constraint_mean", 1]

    result = {
        "spec": "between_country_means",
        "N": len(country_means),
        "beta_constraint": coef,
        "se_constraint": se,
        "t_stat": tstat,
        "p_value": pval,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "R2": fit.rsquared,
        "notes": "Between-country estimator. Country means 2015-2021. HC3 SEs.",
    }

    # Save
    results_df = pd.DataFrame([result])
    out = OUTPUTS_TABLES / "phase1_targeting_between.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out, index=False)
    print(f"\nSaved to {out}")
    print(results_df.to_string())

    return result


if __name__ == "__main__":
    run_between_estimator()
