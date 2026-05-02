"""Mundlak / correlated random effects specification.

Unifies within-country and between-country targeting in a single regression
by including both the time-varying covariate and its country mean, with
year fixed effects. Country fixed effects are omitted (their inclusion would
absorb the country means).

Estimates:
    log(E_rt) = beta_W * (C_rt - Cbar_r) + beta_B * Cbar_r
                + gamma_W * (log G_rt - log Gbar_r) + gamma_B * log Gbar_r
                + theta_t + D_2020 + epsilon_rt

beta_W: within-country effect (should reproduce ~+3.48)
beta_B: between-country effect (should reproduce ~+6.13)

Also computes Wald test of H0: beta_W = beta_B.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def run_mundlak():
    """Run Mundlak correlated random effects specification."""
    print("=" * 60)
    print("MUNDLAK / CORRELATED RANDOM EFFECTS")
    print("=" * 60)

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

    # Country means
    country_means = panel.groupby("country").agg(
        c_bar=("access_to_finance_share", "mean"),
        g_bar=("log_gdp_pc", "mean"),
    )
    panel = panel.merge(country_means, left_on="country", right_index=True)

    # Deviations from means
    panel["c_dev"] = panel["access_to_finance_share"] - panel["c_bar"]
    panel["g_dev"] = panel["log_gdp_pc"] - panel["g_bar"]

    # Year dummies
    year_dummies = pd.get_dummies(panel["year"], prefix="year", drop_first=True).astype(
        int
    )
    panel = pd.concat([panel, year_dummies], axis=1)

    # Note: covid_2020 is collinear with year_2020 dummy, so we drop it
    # Build design matrix
    reg_cols = ["c_dev", "c_bar", "g_dev", "g_bar"] + list(year_dummies.columns)
    df_reg = panel[reg_cols + ["log_eib_per_sme", "country"]].dropna()

    X = df_reg[reg_cols]
    y = df_reg["log_eib_per_sme"]

    # OLS with cluster-robust SEs at country level
    print("\n--- Mundlak specification ---")
    print(f"Observations: {len(df_reg)}")
    print(f"Countries: {df_reg['country'].nunique()}")

    model = sm.OLS(y, X)
    fit = model.fit(cov_type="cluster", cov_kwds={"groups": df_reg["country"]})
    print(fit.summary())

    beta_w = fit.params["c_dev"]
    se_w = fit.bse["c_dev"]
    p_w = fit.pvalues["c_dev"]
    ci_w = fit.conf_int().loc["c_dev"]

    beta_b = fit.params["c_bar"]
    se_b = fit.bse["c_bar"]
    p_b = fit.pvalues["c_bar"]
    ci_b = fit.conf_int().loc["c_bar"]

    print(f"\nWithin effect (beta_W): {beta_w:+.3f}, SE={se_w:.3f}, p={p_w:.4f}")
    print(f"Between effect (beta_B): {beta_b:+.3f}, SE={se_b:.3f}, p={p_b:.4f}")

    # Wald test: H0: beta_W = beta_B
    # Equivalent to testing beta_W - beta_B = 0
    r_matrix = np.array([1, -1] + [0] * (len(reg_cols) - 2))
    wald_test = fit.wald_test(r_matrix, use_f=False, scalar=True)
    wald_stat = float(wald_test.statistic)
    wald_p = float(wald_test.pvalue)

    print("\nWald test H0: beta_W = beta_B")
    print(f"  Chi2(1) = {wald_stat:.3f}, p = {wald_p:.4f}")

    # Save results
    results = {
        "beta_w": beta_w,
        "se_w": se_w,
        "p_w": p_w,
        "ci_w_lower": ci_w[0],
        "ci_w_upper": ci_w[1],
        "beta_b": beta_b,
        "se_b": se_b,
        "p_b": p_b,
        "ci_b_lower": ci_b[0],
        "ci_b_upper": ci_b[1],
        "wald_chi2": wald_stat,
        "wald_p": wald_p,
        "N": len(df_reg),
        "n_countries": df_reg["country"].nunique(),
    }

    df = pd.DataFrame([results])
    out = OUTPUTS_TABLES / "phase1_targeting_mundlak.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nSaved to {out}")

    return results


if __name__ == "__main__":
    run_mundlak()
