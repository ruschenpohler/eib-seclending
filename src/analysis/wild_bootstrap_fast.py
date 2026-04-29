"""Fast wild cluster bootstrap for Phase 1 regressions.

Uses the Frisch-Waugh-Lovell theorem: demean data once (absorb FE), then
run OLS on demeaned data for each bootstrap rep. This avoids re-computing
fixed effects 9,999 times.

Weights: Rademacher (-1, +1) with equal probability.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def demean_two_way(df, y_col, x_cols, fe1, fe2):
    """Two-way demeaning: y - y_bar_fe1 - y_bar_fe2 + y_bar_overall."""
    df = df.copy()
    for col in [y_col] + x_cols:
        overall = df[col].mean()
        bar1 = df.groupby(fe1)[col].transform("mean")
        bar2 = df.groupby(fe2)[col].transform("mean")
        df[f"{col}_dm"] = df[col] - bar1 - bar2 + overall
    return df


def cluster_robust_se(X, resid, clusters):
    """Compute cluster-robust variance matrix."""
    n, k = X.shape
    bread = np.linalg.inv(X.T @ X)
    meat = np.zeros((k, k))
    for c in np.unique(clusters):
        mask = clusters == c
        Xc = X[mask]
        rc = resid[mask]
        meat += Xc.T @ np.outer(rc, rc) @ Xc
    var = bread @ meat @ bread
    return np.sqrt(np.diag(var))


def wild_bootstrap_fast(df, formula, param, cluster_var="country", n_reps=999, seed=42):
    """Fast wild cluster bootstrap using pre-demeaned data."""
    rng = np.random.default_rng(seed)

    # Parse formula
    parts = formula.split("|")
    y_x = parts[0].strip()
    fe = parts[1].strip() if len(parts) > 1 else ""
    y_col = y_x.split("~")[0].strip()
    rhs = y_x.split("~")[1].strip()
    x_cols = [c.strip() for c in rhs.split("+")]
    fe_vars = [c.strip() for c in fe.split("+")]

    # Drop rows with missing values
    all_cols = list(dict.fromkeys([y_col] + x_cols + fe_vars + [cluster_var]))
    df_clean = df[all_cols].dropna()

    # Two-way demeaning
    df_dm = demean_two_way(df_clean, y_col, x_cols, fe_vars[0], fe_vars[1])
    y_dm = df_dm[f"{y_col}_dm"].to_numpy()
    # No constant in demeaned FE regression
    X_dm = np.column_stack([df_dm[f"{c}_dm"].to_numpy() for c in x_cols])
    x_names = x_cols
    clusters = df_dm[cluster_var].astype("category").cat.codes.to_numpy()
    n_clusters = df_dm[cluster_var].nunique()

    # Original estimate
    beta = np.linalg.lstsq(X_dm, y_dm, rcond=None)[0]
    resid = y_dm - X_dm @ beta
    se = cluster_robust_se(X_dm, resid, clusters)
    param_idx = x_names.index(param)
    t_orig = beta[param_idx] / se[param_idx]

    # Bootstrap
    t_boots = []
    for _ in range(n_reps):
        weights = rng.choice([-1.0, 1.0], size=n_clusters)
        w = weights[clusters]
        y_star = y_dm + resid * w
        beta_b = np.linalg.lstsq(X_dm, y_star, rcond=None)[0]
        resid_b = y_star - X_dm @ beta_b
        se_b = cluster_robust_se(X_dm, resid_b, clusters)
        if se_b[param_idx] > 0:
            t_boots.append(beta_b[param_idx] / se_b[param_idx])

    t_boots = np.array(t_boots)
    p_bootstrap = np.mean(np.abs(t_boots) >= np.abs(t_orig))

    return {
        "spec": "",
        "param": param,
        "coef": beta[param_idx],
        "se": se[param_idx],
        "t_analytic": t_orig,
        "p_analytic": 2 * (1 - np.mean(np.abs(t_boots) >= 0)),  # placeholder
        "p_bootstrap": p_bootstrap,
        "n_reps": n_reps,
        "n_successful": len(t_boots),
    }


def main():
    print("=" * 60)
    print("FAST WILD CLUSTER BOOTSTRAP — PHASE 1 (999 reps)")
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
    panel["covid_2020"] = (panel["year"] == 2020).astype(int)

    results = []

    # Spec 1a (drop covid_2020 — absorbed by year FE)
    df1a = panel.dropna(
        subset=["log_eib_per_sme", "access_to_finance_share", "log_gdp_pc"]
    )
    print("\n--- Spec 1a ---")
    r = wild_bootstrap_fast(
        df1a,
        "log_eib_per_sme ~ access_to_finance_share + log_gdp_pc | country + year",
        "access_to_finance_share",
    )
    r["spec"] = "Spec 1a"
    results.append(r)
    print(f"  Coef: {r['coef']:.3f}, SE: {r['se']:.3f}, t: {r['t_analytic']:.3f}")
    print(
        f"  Bootstrap p: {r['p_bootstrap']:.4f} ({r['n_successful']}/{r['n_reps']} successful)"
    )

    # Spec 1b
    pl = panel.sort_values(["country", "year"])
    pl["access_to_finance_share_lag1"] = pl.groupby("country")[
        "access_to_finance_share"
    ].shift(1)
    df1b = pl.dropna(
        subset=["log_eib_per_sme", "access_to_finance_share_lag1", "log_gdp_pc"]
    )
    print("\n--- Spec 1b ---")
    r = wild_bootstrap_fast(
        df1b,
        "log_eib_per_sme ~ access_to_finance_share_lag1 + log_gdp_pc | country + year",
        "access_to_finance_share_lag1",
    )
    r["spec"] = "Spec 1b"
    results.append(r)
    print(f"  Coef: {r['coef']:.3f}, SE: {r['se']:.3f}, t: {r['t_analytic']:.3f}")
    print(
        f"  Bootstrap p: {r['p_bootstrap']:.4f} ({r['n_successful']}/{r['n_reps']} successful)"
    )

    # Spec 2a — Plausibility (industry investment rate)
    panel["industry_investment_rate_w"] = panel["industry_investment_rate"].clip(
        panel["industry_investment_rate"].quantile(0.01),
        panel["industry_investment_rate"].quantile(0.99),
    )
    panel_pl = panel.sort_values(["country", "year"])
    panel_pl["log_eib_per_sme_lag1"] = panel_pl.groupby("country")[
        "log_eib_per_sme"
    ].shift(1)
    panel_pl["access_to_finance_share_lag1"] = panel_pl.groupby("country")[
        "access_to_finance_share"
    ].shift(1)
    panel_pl["log_gdp_pc_lag1"] = panel_pl.groupby("country")["log_gdp_pc"].shift(1)
    df2a = panel_pl[panel_pl["year"].isin([2016, 2017, 2018, 2019, 2020])].dropna(
        subset=[
            "industry_investment_rate_w",
            "log_eib_per_sme_lag1",
            "access_to_finance_share_lag1",
            "log_gdp_pc",
        ]
    )
    print("\n--- Spec 2a: Industry investment rate ---")
    r = wild_bootstrap_fast(
        df2a,
        "industry_investment_rate_w ~ log_eib_per_sme_lag1 + access_to_finance_share_lag1 + log_gdp_pc | country + year",
        "log_eib_per_sme_lag1",
    )
    r["spec"] = "Spec 2a"
    results.append(r)
    print(f"  Coef: {r['coef']:.3f}, SE: {r['se']:.3f}, t: {r['t_analytic']:.3f}")
    print(
        f"  Bootstrap p: {r['p_bootstrap']:.4f} ({r['n_successful']}/{r['n_reps']} successful)"
    )

    # Spec 2b — Plausibility (firm entry rate)
    panel_pl["firm_entry_rate_w"] = panel_pl["firm_entry_rate"].clip(
        panel_pl["firm_entry_rate"].quantile(0.01),
        panel_pl["firm_entry_rate"].quantile(0.99),
    )
    df2b = panel_pl[panel_pl["year"].isin([2016, 2017, 2018, 2019, 2020])].dropna(
        subset=[
            "firm_entry_rate_w",
            "log_eib_per_sme_lag1",
            "access_to_finance_share_lag1",
            "log_gdp_pc",
        ]
    )
    print("\n--- Spec 2b: Firm entry rate ---")
    r = wild_bootstrap_fast(
        df2b,
        "firm_entry_rate_w ~ log_eib_per_sme_lag1 + access_to_finance_share_lag1 + log_gdp_pc | country + year",
        "log_eib_per_sme_lag1",
    )
    r["spec"] = "Spec 2b"
    results.append(r)
    print(f"  Coef: {r['coef']:.3f}, SE: {r['se']:.3f}, t: {r['t_analytic']:.3f}")
    print(
        f"  Bootstrap p: {r['p_bootstrap']:.4f} ({r['n_successful']}/{r['n_reps']} successful)"
    )

    # Save
    df = pd.DataFrame(results)
    out = OUTPUTS_TABLES / "phase1_wild_bootstrap.csv"
    df.to_csv(out, index=False)
    print(f"\n{'='*60}")
    print(f"Saved to {out}")
    print(f"{'='*60}")
    print(df.to_string())


if __name__ == "__main__":
    main()
