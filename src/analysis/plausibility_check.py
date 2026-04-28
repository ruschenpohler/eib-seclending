"""Plausibility check (Spec 2) — correlational co-movement test.

Tests whether lagged EIB lending intensity predicts subsequent SME outcomes,
conditioning on lagged constraint severity, GDP per capita, and fixed effects.

THIS IS A CORRELATIONAL TEST — NOT CAUSAL. All outputs are labelled accordingly.
See prespec-plan.md Spec 2 for full pre-registration.

Outcomes:
    1. SME investment rate: gross investment in tangible goods / value added,
       Eurostat SBS table sbs_na_ind_r2, NACE B+C+D+E (industry aggregate).
       NOTE: This includes all firm sizes, not only SMEs, because V15110 is
       unavailable at the SME size class in Eurostat.
    2. Firm entry rate: enterprise births / active enterprise stock,
       Eurostat business demography bd_9bd_sz_cl_r2, size class GE10 (>=10 emp).
       NOTE: Eurostat does not provide a 0-249 size class in this table.

Temporal alignment:
    EIB intensity and constraints at t-1  ->  outcomes at t
    Panel: 2016-2020 (outcome years), with lags from 2015-2019.

Cross-region placebo:
    For each country r, use leave-one-out average of all other countries'
    lagged EIB intensity (unweighted). Tests whether the co-movement is
    specific to own EIB exposure or driven by a common eurozone factor.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import pyfixest as pf

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def create_lags(df, vars_to_lag, id_col="country", time_col="year"):
    """Create one-year lags for specified variables."""
    df = df.sort_values([id_col, time_col])
    for v in vars_to_lag:
        df[f"{v}_lag1"] = df.groupby(id_col)[v].shift(1)
    return df


def create_placebo(df, var="log_eib_per_sme_lag1", id_col="country", time_col="year"):
    """Leave-one-out average of var for all other countries in same year."""
    df = df.sort_values([time_col, id_col])
    # For each year, compute mean across all countries
    year_means = df.groupby(time_col)[var].transform("mean")
    # Leave-one-out: (N * mean - own_value) / (N - 1)
    n_per_year = df.groupby(time_col)[var].transform("count")
    df[f"{var}_placebo"] = (n_per_year * year_means - df[var]) / (n_per_year - 1)
    return df


def winsorize(s, lower=0.01, upper=0.99):
    """Winsorize at 1st and 99th percentile."""
    lo, hi = s.quantile([lower, upper])
    return s.clip(lo, hi)


def run_plausibility_check():
    print("=" * 70)
    print("PLAUSIBILITY CHECK (Spec 2) — CORRELATIONAL, NOT CAUSAL")
    print("=" * 70)

    # Load panel
    panel = pd.read_csv(DATA_PROCESSED / "eib_analysis_panel.csv")
    panel = panel.dropna(subset=["country", "year"])
    panel["year"] = panel["year"].astype(int)

    # Winsorize outcomes at 1st/99th percentile (pre-registered)
    panel["industry_investment_rate_w"] = winsorize(panel["industry_investment_rate"])
    panel["firm_entry_rate_w"] = winsorize(panel["firm_entry_rate"])

    # Create lags
    panel = create_lags(
        panel,
        ["log_eib_per_sme", "eib_per_sme", "access_to_finance_share", "gdp_per_capita"],
    )
    panel["log_gdp_pc_lag1"] = np.log(panel["gdp_per_capita_lag1"])

    # COVID 2020 indicator (pre-registered: unconditional in primary specs)
    panel["covid_2020"] = (panel["year"] == 2020).astype(int)

    # Create placebo (leave-one-out average EIB intensity)
    panel = create_placebo(panel, var="log_eib_per_sme_lag1")

    # Subset to years where outcomes are available and lags exist
    # SBS outcomes end in 2020, so usable outcome years: 2016-2020
    reg_df = panel[panel["year"].isin([2016, 2017, 2018, 2019, 2020])].copy()

    # Further require non-missing lagged regressors
    reg_df = reg_df.dropna(
        subset=[
            "industry_investment_rate_w",
            "firm_entry_rate_w",
            "log_eib_per_sme_lag1",
            "access_to_finance_share_lag1",
            "log_gdp_pc_lag1",
            "country",
            "year",
        ]
    )

    print(f"\nRegression panel: {len(reg_df)} observations")
    print(f"Countries: {reg_df['country'].nunique()}")
    print(f"Years: {sorted(reg_df['year'].unique())}")

    results = []

    def run_one_spec(data, outcome_var, label, placebo=False, notes=""):
        """Run one specification and append to results."""
        eib_var = "log_eib_per_sme_lag1_placebo" if placebo else "log_eib_per_sme_lag1"
        spec_label = f"{label}_placebo" if placebo else label

        df = data.dropna(
            subset=[
                outcome_var,
                eib_var,
                "access_to_finance_share_lag1",
                "log_gdp_pc_lag1",
            ]
        )
        if len(df) < 30:
            print(f"  [SKIP] {spec_label}: only {len(df)} obs")
            return

        print(f"\n--- {spec_label} ---")
        print(f"  Outcome: {outcome_var}")
        print(f"  EIB variable: {eib_var}")
        print(f"  Observations: {len(df)}")

        try:
            fit = pf.feols(
                f"{outcome_var} ~ {eib_var} + access_to_finance_share_lag1 + log_gdp_pc_lag1 + covid_2020 | country + year",
                data=df,
                vcov={"CRV1": "country"},
            )
            print(fit.summary())

            coef = fit.coef().get(eib_var, np.nan)
            se = fit.se().get(eib_var, np.nan)
            tstat = fit.tstat().get(eib_var, np.nan)
            pval = fit.pvalue().get(eib_var, np.nan)
            r2 = getattr(fit, "_r2", np.nan)

            results.append(
                {
                    "outcome_var": outcome_var,
                    "spec": spec_label,
                    "N": len(df),
                    "beta_eib_intensity": coef,
                    "se": se,
                    "t_stat": tstat,
                    "p_value": pval,
                    "R2": r2,
                    "notes": notes,
                }
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append(
                {
                    "outcome_var": outcome_var,
                    "spec": spec_label,
                    "N": len(df),
                    "notes": f"ERROR: {e}",
                }
            )

    # ---- Primary specifications ----

    run_one_spec(
        reg_df,
        "industry_investment_rate_w",
        "2a_industry_investment_rate",
        notes=(
            "CORRELATIONAL — NOT CAUSAL. "
            "Outcome = V15110/V12110 for NACE B,C,D,E (industry aggregate, all firm sizes). "
            "V15110 unavailable at SME size class; services excluded."
        ),
    )

    run_one_spec(
        reg_df,
        "firm_entry_rate_w",
        "2b_firm_entry_rate",
        notes=(
            "CORRELATIONAL — NOT CAUSAL. "
            "Outcome = V11920/V11910 for size class GE10 (>=10 employees). "
            "Eurostat does not provide 0-249 size class."
        ),
    )

    # ---- Cross-region placebo ----

    run_one_spec(
        reg_df,
        "industry_investment_rate_w",
        "2a_industry_investment_rate",
        placebo=True,
        notes=(
            "CROSS-REGION PLACEBO — diagnostic only, not a causal test. "
            "Outcome regressed on leave-one-out average EIB intensity of all other countries."
        ),
    )

    run_one_spec(
        reg_df,
        "firm_entry_rate_w",
        "2b_firm_entry_rate",
        placebo=True,
        notes=(
            "CROSS-REGION PLACEBO — diagnostic only, not a causal test. "
            "Outcome regressed on leave-one-out average EIB intensity of all other countries."
        ),
    )

    # Save
    results_df = pd.DataFrame(results)
    out = OUTPUTS_TABLES / "phase1_plausibility_check.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out, index=False)
    print(f"\n{'='*70}")
    print(f"Saved results to {out}")
    print(f"{'='*70}")
    print(results_df.to_string())

    return results_df


if __name__ == "__main__":
    run_plausibility_check()
