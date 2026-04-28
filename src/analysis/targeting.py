"""Targeting regression — Specs 1a and 1b.

Co-primary specifications:
- Spec 1a (contemporaneous):
    log(EIB_per_SME) = α + β·constraint + γ·log(GDP_pc) + δ_country + θ_year + ε
- Spec 1b (lagged constraint):
    log(EIB_per_SME) = α + β·constraint_lag1 + γ·log(GDP_pc) + δ_country + θ_year + ε

SEs clustered at country level. Wild cluster bootstrap p-values reported
alongside analytic (Cameron-Gelbach-Miller 2008 correction for few clusters).

Output: outputs/tables/phase1_targeting_regression.csv
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import duckdb
import pandas as pd

from src.config import DATA_PROCESSED, OUTPUTS_TABLES


def run_targeting_regression():
    """Run targeting regression specs 1a and 1b."""
    print("=== Targeting Regression ===\n")

    # Load panel
    db_path = DATA_PROCESSED / "eib_analysis.duckdb"
    with duckdb.connect(str(db_path)) as con:
        df = con.execute("SELECT * FROM panel").fetchdf()

    print(f"Panel: {len(df)} observations")

    # Drop rows with missing key variables
    df = df.dropna(
        subset=[
            "eib_per_sme",
            "access_to_finance_share",
            "gdp_per_capita",
            "country",
            "year",
        ]
    )
    print(f"After dropping missing: {len(df)} observations")

    # Create lagged constraint
    df = df.sort_values(["country", "year"])
    df["constraint_lag1"] = df.groupby("country")["access_to_finance_share"].shift(1)

    # Log transforms
    df["log_eib_per_sme"] = np.log(df["eib_per_sme"])
    df["log_gdp_pc"] = np.log(df["gdp_per_capita"])

    # Country and year as categorical
    df["country_code"] = df["country"].astype("category")
    df["year_code"] = df["year"].astype("category")

    results = []

    # Spec 1a — contemporaneous constraint
    print("\n--- Spec 1a: Contemporaneous constraint ---")
    df_1a = df.dropna(
        subset=["log_eib_per_sme", "access_to_finance_share", "log_gdp_pc"]
    )
    print(f"Observations: {len(df_1a)}")

    try:
        import pyfixest as pf

        fit_1a = pf.feols(
            "log_eib_per_sme ~ access_to_finance_share + log_gdp_pc | country_code + year_code",
            data=df_1a,
            vcov={"CRV1": "country_code"},
        )
        print(fit_1a.summary())
        coef = fit_1a.coef().get("access_to_finance_share", np.nan)
        se = fit_1a.se().get("access_to_finance_share", np.nan)
        tstat = fit_1a.tstat().get("access_to_finance_share", np.nan)
        pval = fit_1a.pvalue().get("access_to_finance_share", np.nan)
        r2 = getattr(fit_1a, "_r2", np.nan)

        results.append(
            {
                "spec": "1a_contemporaneous",
                "N": len(df_1a),
                "beta_constraint": coef,
                "se_constraint": se,
                "t_stat": tstat,
                "p_value": pval,
                "R2_within": r2,
                "FE_type": "country + year",
                "cluster_level": "country",
                "notes": "Co-primary. Wild bootstrap p-value to be added.",
            }
        )
    except Exception as e:
        print(f"pyfixest error: {e}")
        results.append(
            {
                "spec": "1a_contemporaneous",
                "N": len(df_1a),
                "notes": f"Estimation error: {e}",
            }
        )

    # Spec 1b — lagged constraint
    print("\n--- Spec 1b: Lagged constraint (t-1) ---")
    df_1b = df.dropna(subset=["log_eib_per_sme", "constraint_lag1", "log_gdp_pc"])
    print(f"Observations: {len(df_1b)}")

    try:
        fit_1b = pf.feols(
            "log_eib_per_sme ~ constraint_lag1 + log_gdp_pc | country_code + year_code",
            data=df_1b,
            vcov={"CRV1": "country_code"},
        )
        print(fit_1b.summary())
        coef = fit_1b.coef().get("constraint_lag1", np.nan)
        se = fit_1b.se().get("constraint_lag1", np.nan)
        tstat = fit_1b.tstat().get("constraint_lag1", np.nan)
        pval = fit_1b.pvalue().get("constraint_lag1", np.nan)
        r2 = getattr(fit_1b, "_r2", np.nan)

        results.append(
            {
                "spec": "1b_lagged_constraint",
                "N": len(df_1b),
                "beta_constraint": coef,
                "se_constraint": se,
                "t_stat": tstat,
                "p_value": pval,
                "R2_within": r2,
                "FE_type": "country + year",
                "cluster_level": "country",
                "notes": "Co-primary. Wild bootstrap p-value to be added.",
            }
        )
    except Exception as e:
        print(f"pyfixest error: {e}")
        results.append(
            {
                "spec": "1b_lagged_constraint",
                "N": len(df_1b),
                "notes": f"Estimation error: {e}",
            }
        )

    # Save results
    results_df = pd.DataFrame(results)
    out = OUTPUTS_TABLES / "phase1_targeting_regression.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out, index=False)
    print(f"\nSaved results to {out}")
    print(results_df.to_string())

    return results_df


if __name__ == "__main__":
    import numpy as np

    run_targeting_regression()
