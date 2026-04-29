"""Add confidence intervals and MDE to existing targeting results tables.

Reads existing output tables, computes 95% CIs analytically, and saves
updated versions. Does not re-run regressions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd

from src.config import OUTPUTS_TABLES


def add_ci_to_table(df, beta_col="beta_constraint", se_col="se_constraint", n_col="N"):
    """Add 95% CI columns using t-distribution."""
    df = df.copy()

    # Degrees of freedom: N - k, where k is roughly 5 (constraint, GDP, FE)
    # For country FE with 27 countries, we lose 26 df; for year FE with 7 years, 6 df
    # But the t-stat from the regression already accounts for this via CRV1
    # We'll use the df implied by N and approximate k=5 regressors + 27 country FE + 6 year FE = 38
    # Actually, for simplicity, use normal approx for N>100, t for smaller N
    def get_ci(row):
        beta = row[beta_col]
        se = row[se_col]
        n = row[n_col]
        if pd.isna(beta) or pd.isna(se) or se <= 0:
            return pd.Series([np.nan, np.nan])
        # Approximate df: N - 38 (5 regressors + 27 country dummies + 6 year dummies)
        df_est = max(n - 38, 5)
        if df_est > 100:
            t_crit = 1.96
        else:
            from scipy import stats

            t_crit = stats.t.ppf(0.975, df_est)
        lower = beta - t_crit * se
        upper = beta + t_crit * se
        return pd.Series([lower, upper])

    df[["ci_lower", "ci_upper"]] = df.apply(get_ci, axis=1)
    return df


def compute_mde(se, df_est):
    """Compute minimum detectable effect at 80% power, alpha=0.05."""
    from scipy import stats

    t_alpha = stats.t.ppf(0.975, df_est)
    t_power = stats.t.ppf(0.80, df_est)
    return (t_alpha + t_power) * se


def main():
    print("Adding CIs to existing targeting results...")

    # Main targeting table
    targeting = pd.read_csv(OUTPUTS_TABLES / "phase1_targeting_regression.csv")
    targeting = add_ci_to_table(targeting)
    # MDE for contemporaneous spec
    se_contemp = targeting[targeting["spec"] == "1a_contemporaneous"][
        "se_constraint"
    ].values[0]
    n_contemp = targeting[targeting["spec"] == "1a_contemporaneous"]["N"].values[0]
    mde = compute_mde(se_contemp, max(n_contemp - 38, 5))
    print(f"MDE (contemporaneous): {mde:.2f}")
    targeting["mde_80"] = np.nan
    targeting.loc[targeting["spec"] == "1a_contemporaneous", "mde_80"] = mde
    targeting.to_csv(OUTPUTS_TABLES / "phase1_targeting_regression.csv", index=False)
    print("Updated phase1_targeting_regression.csv")

    # Robustness table
    robustness = pd.read_csv(OUTPUTS_TABLES / "phase1_targeting_robustness.csv")
    robustness = add_ci_to_table(robustness)
    robustness.to_csv(OUTPUTS_TABLES / "phase1_targeting_robustness.csv", index=False)
    print("Updated phase1_targeting_robustness.csv")

    # Print summary for README update
    print("\n" + "=" * 60)
    print("CI SUMMARY FOR README")
    print("=" * 60)
    for _, row in targeting.iterrows():
        print(
            f"{row['spec']}: beta={row['beta_constraint']:.2f}, 95% CI=[{row['ci_lower']:.2f}, {row['ci_upper']:.2f}]"
        )
    print(f"\nMDE at 80% power: {mde:.2f}")
    print(
        f"Interpretation: a {mde:.1f} percentage-point increase in constraint share predicts"
    )
    print("a 1 log-point increase in EIB per SME.")


if __name__ == "__main__":
    main()
