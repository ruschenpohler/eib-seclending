"""Verify why Mundlak beta_W (+5.16) differs from primary FE beta (+3.48).

The Mundlak uses year FE only (c_dev = C_rt - Cbar_r).
The primary spec uses two-way FE (country + year), equivalent to using
two-way demeaned C: C_rt - Cbar_r - Cbar_t + Cbar_overall.

This script decomposes the difference by:
1. Manually computing both coefficients from demeaned data
2. Computing the variance of the regressor under both demeaning schemes
3. Checking whether the coefficient gap is explained by additional FE
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.config import DATA_PROCESSED


def demean_one_way(df, col, fe_col):
    """Demean by one FE dimension."""
    return df[col] - df.groupby(fe_col)[col].transform("mean")


def demean_two_way(df, col, fe1, fe2):
    """Two-way demeaning: y - y_bar_fe1 - y_bar_fe2 + y_bar_overall."""
    overall = df[col].mean()
    bar1 = df.groupby(fe1)[col].transform("mean")
    bar2 = df.groupby(fe2)[col].transform("mean")
    return df[col] - bar1 - bar2 + overall


def run_gap_analysis():
    print("=" * 70)
    print("DECOMPOSING THE MUNDLAK vs PRIMARY SPEC GAP")
    print("=" * 70)

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
    panel["log_eib"] = np.log(panel["eib_per_sme"])
    panel["log_gdp"] = np.log(panel["gdp_per_capita"])
    panel["covid"] = (panel["year"] == 2020).astype(int)

    # Country and year as categorical for groupby
    panel["country_code"] = panel["country"].astype("category")
    panel["year_code"] = panel["year"].astype("category")

    # --- 1. Primary spec: two-way FE ---
    print("\n--- 1. Primary spec (two-way FE) ---")
    df = panel.copy()
    df["c_2way"] = demean_two_way(
        df, "access_to_finance_share", "country_code", "year_code"
    )
    df["y_2way"] = demean_two_way(df, "log_eib", "country_code", "year_code")
    df["g_2way"] = demean_two_way(df, "log_gdp", "country_code", "year_code")
    df["covid_2way"] = demean_two_way(df, "covid", "country_code", "year_code")

    # OLS on two-way demeaned data (no constant)
    X = df[["c_2way", "g_2way", "covid_2way"]].dropna()
    y = df["y_2way"].loc[X.index]
    fit_2way = sm.OLS(y, X).fit()
    beta_2way = fit_2way.params["c_2way"]
    print(f"beta_2way = {beta_2way:+.4f}")
    print(f"  SE = {fit_2way.bse['c_2way']:.4f}")
    print(f"  Var(c_2way) = {df['c_2way'].var():.6f}")
    print(f"  R2 = {fit_2way.rsquared:.4f}")

    # --- 2. Mundlak spec: one-way demeaning + year FE ---
    print("\n--- 2. Mundlak (one-way demeaning + year FE) ---")
    df["c_1way"] = demean_one_way(df, "access_to_finance_share", "country_code")
    df["y_1way"] = demean_one_way(df, "log_eib", "country_code")
    df["g_1way"] = demean_one_way(df, "log_gdp", "country_code")
    df["covid_1way"] = demean_one_way(df, "covid", "country_code")

    # Year dummies
    year_dummies = pd.get_dummies(
        df["year_code"], prefix="year", drop_first=True
    ).astype(int)
    df = pd.concat([df, year_dummies], axis=1)
    year_cols = list(year_dummies.columns)

    # OLS on one-way demeaned data + year FE (no constant, no country FE)
    reg_cols = ["c_1way", "g_1way", "covid_1way"] + year_cols
    X_m = df[reg_cols].dropna()
    y_m = df["y_1way"].loc[X_m.index]
    fit_1way = sm.OLS(y_m, X_m).fit()
    beta_1way = fit_1way.params["c_1way"]
    print(f"beta_1way = {beta_1way:+.4f}")
    print(f"  SE = {fit_1way.bse['c_1way']:.4f}")
    print(f"  Var(c_1way) = {df['c_1way'].var():.6f}")
    print(f"  R2 = {fit_1way.rsquared:.4f}")

    # --- 3. Pure one-way (no year FE) ---
    print("\n--- 3. Pure one-way demeaning (no year FE) ---")
    X_pure = df[["c_1way", "g_1way", "covid_1way"]].dropna()
    y_pure = df["y_1way"].loc[X_pure.index]
    fit_pure = sm.OLS(y_pure, X_pure).fit()
    beta_pure = fit_pure.params["c_1way"]
    print(f"beta_pure_1way = {beta_pure:+.4f}")
    print(f"  SE = {fit_pure.bse['c_1way']:.4f}")

    # --- 4. Variance decomposition of the regressor ---
    print("\n--- 4. Variance decomposition of constraint variable ---")
    var_total = df["access_to_finance_share"].var()
    var_1way = df["c_1way"].var()
    var_2way = df["c_2way"].var()

    print(f"Var(C_total) = {var_total:.6f}")
    print(f"Var(C_1way) = {var_1way:.6f} ({100*var_1way/var_total:.1f}% of total)")
    print(f"Var(C_2way) = {var_2way:.6f} ({100*var_2way/var_total:.1f}% of total)")
    print(
        f"Var lost: 1way -> 2way = {var_1way - var_2way:.6f} ({100*(var_1way-var_2way)/var_1way:.1f}% of 1way)"
    )

    # --- 5. What do year FE absorb from the one-way demeaned regressor? ---
    print("\n--- 5. Year FE absorption from one-way demeaned C ---")
    # Regress c_1way on year dummies to get the part absorbed by year FE
    X_yr = df[year_cols].dropna()
    c_yr = df["c_1way"].loc[X_yr.index]
    fit_yr = sm.OLS(c_yr, X_yr).fit()
    c_yr_pred = fit_yr.predict(X_yr)
    c_yr_resid = c_yr - c_yr_pred

    var_absorbed_by_year = c_yr_pred.var()
    var_residual = c_yr_resid.var()
    print(f"Var in c_1way absorbed by year FE = {var_absorbed_by_year:.6f}")
    print(f"Var in c_1way residual after year FE = {var_residual:.6f}")
    print(f"Share absorbed by year FE = {100*var_absorbed_by_year/var_1way:.1f}%")

    # --- 6. Is the coefficient gap explained by variance loss? ---
    print("\n--- 6. Does variance loss explain the coefficient gap? ---")
    # If beta ~ Cov(X,Y)/Var(X), and the signal in X is reduced by year FE,
    # the coefficient should change proportionally if Cov(X,Y) is also reduced
    # by the same amount.

    # Compute Cov(c, y) for both specifications
    cov_1way = np.cov(df["c_1way"], df["y_1way"])[0, 1]
    cov_2way = np.cov(df["c_2way"], df["y_2way"])[0, 1]

    print(f"Cov(c_1way, y_1way) = {cov_1way:.6f}")
    print(f"Cov(c_2way, y_2way) = {cov_2way:.6f}")
    print(f"Cov ratio (2way/1way) = {cov_2way/cov_1way:.3f}")
    print(f"Var ratio (2way/1way) = {var_2way/var_1way:.3f}")
    print(
        f"Predicted beta ratio (Cov/Var) = {(cov_2way/var_2way)/(cov_1way/var_1way):.3f}"
    )
    print(f"Actual beta ratio = {beta_2way/beta_1way:.3f}")

    # --- 7. Check: does pyfixest match manual 2way? ---
    print("\n--- 7. Verify pyfixest matches manual 2way ---")
    try:
        import pyfixest as pf

        fit_pf = pf.feols(
            "log_eib ~ access_to_finance_share + log_gdp | country_code + year_code",
            data=df,
            vcov={"CRV1": "country_code"},
        )
        beta_pf = fit_pf.coef()["access_to_finance_share"]
        print(f"pyfixest beta = {beta_pf:+.4f}")
        print(f"Manual beta = {beta_2way:+.4f}")
        print(f"Difference = {abs(beta_pf - beta_2way):.6f}")
    except Exception as e:
        print(f"pyfixest error: {e}")

    # --- 8. Check: does Mundlak with constant give same as without? ---
    print("\n--- 8. Mundlak with explicit constant ---")
    X_m_const = sm.add_constant(df[reg_cols].dropna())
    y_m_const = df["y_1way"].loc[X_m_const.index]
    fit_m_const = sm.OLS(y_m_const, X_m_const).fit()
    print(f"Mundlak with constant: beta_W = {fit_m_const.params['c_1way']:+.4f}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Primary 2-way FE beta = {beta_2way:+.4f}")
    print(f"Mundlak 1-way + year FE beta = {beta_1way:+.4f}")
    print(f"Gap = {beta_1way - beta_2way:+.4f}")
    print(
        f"\nYear FE absorb {100*var_absorbed_by_year/var_1way:.1f}% of the one-way within variance"
    )
    print(f"Actual beta ratio (2way/1way) = {beta_2way/beta_1way:.3f}")
    print(
        f"Predicted from Cov/Var ratio = {(cov_2way/var_2way)/(cov_1way/var_1way):.3f}"
    )


if __name__ == "__main__":
    run_gap_analysis()
