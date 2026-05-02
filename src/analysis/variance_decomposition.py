"""Variance decomposition of key panel variables.

Computes between-country vs within-country variance shares for:
- Constraint share (C_rt)
- Log EIB intensity per SME (log E_rt)
- Log GDP per capita (log G_rt)

Also computes intraclass correlation coefficient (ICC) from random-intercept model.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def variance_decomposition(df, var, id_col="country"):
    """Compute between and within variance shares."""
    # Between variance: Var(mean by group)
    group_means = df.groupby(id_col)[var].mean()
    between_var = group_means.var(ddof=1)

    # Within variance: mean of Var within each group
    within_vars = df.groupby(id_col)[var].var(ddof=1)
    within_var = within_vars.mean()

    # Total variance
    total_var = df[var].var(ddof=1)

    # Alternative: law of total variance
    # Var(Y) = E[Var(Y|group)] + Var(E[Y|group])
    # = within_var + between_var

    between_share = between_var / total_var if total_var > 0 else np.nan
    within_share = within_var / total_var if total_var > 0 else np.nan

    return {
        "variable": var,
        "between_var": between_var,
        "within_var": within_var,
        "total_var": total_var,
        "between_share": between_share,
        "within_share": within_share,
    }


def compute_icc(df, var, id_col="country"):
    """Compute intraclass correlation coefficient from one-way ANOVA."""
    from scipy import stats

    groups = df.groupby(id_col)[var].apply(list)
    # One-way ANOVA
    f_stat, p_val = stats.f_oneway(*groups)

    # ICC = (MSB - MSW) / (MSB + (n_0 - 1) * MSW)
    # where n_0 is a function of group sizes
    group_stats = df.groupby(id_col)[var].agg(["count", "mean", "var"])
    n = len(df)
    k = len(group_stats)

    msb = (
        group_stats["count"].values * (group_stats["mean"].values - df[var].mean()) ** 2
    )
    msb = msb.sum() / (k - 1)

    msw = ((group_stats["count"].values - 1) * group_stats["var"].values).sum() / (
        n - k
    )

    # Simplified ICC for balanced panel
    n_avg = n / k
    icc = (msb - msw) / (msb + (n_avg - 1) * msw)

    return icc


def main():
    print("=" * 60)
    print("VARIANCE DECOMPOSITION")
    print("=" * 60)

    panel = pd.read_csv(DATA_PROCESSED / "eib_analysis_panel.csv")
    panel = panel.dropna(
        subset=["eib_per_sme", "access_to_finance_share", "gdp_per_capita", "country"]
    )
    panel["log_eib_per_sme"] = np.log(panel["eib_per_sme"])
    panel["log_gdp_pc"] = np.log(panel["gdp_per_capita"])

    results = []
    for var in ["access_to_finance_share", "log_eib_per_sme", "log_gdp_pc"]:
        res = variance_decomposition(panel, var)
        res["icc"] = compute_icc(panel, var)
        results.append(res)

    df = pd.DataFrame(results)
    print("\nVariance decomposition:")
    print(df.to_string(index=False))

    out = OUTPUTS_TABLES / "phase1_variance_decomposition.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved to {out}")

    return df


if __name__ == "__main__":
    main()
