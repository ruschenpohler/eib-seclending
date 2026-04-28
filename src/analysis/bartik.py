"""Build Bartik instrument and run 2SLS (Spec 3, Phase 2b).

Bartik_rt = Σ_j (employment_share_jr,2015 × EIB_sectoral_lending_jt)

where j = NACE section (intersection of SBS and EIB crosswalk),
      employment_share from Eurostat SBS V16110 (persons employed),
      size classes 10-19, 20-49, 50-249 aggregated,
      base year = 2015,
      EIB_sectoral_lending = EU-aggregate signed amount by NACE section × year.

First stage:
    EIB_per_SME_rt = π·Bartik_rt + γ·log(GDP_pc_rt) + δ_r + θ_t + covid_2020 + u_rt

Second stage:
    constraint_rt = β·EIB_per_SME_hat_rt + γ·log(GDP_pc_rt) + δ_r + θ_t + covid_2020 + ε_rt

Pass criterion: K-P rk Wald F > 10 (cluster-robust).
Expected sign: β < 0.

Exclusion restriction test (mandatory):
    ΔEIB_volume_rt = α + π·Bartik_rt + β·sector_growth_residual_rt
                     + δ_r + θ_t + ε_rt
    Test H₀: β = 0. If rejected (p < 0.10), instrument invalid.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
from pyfixest.estimation import feols

from src.config import DATA_RAW, DATA_PROCESSED, DATA_INTERIM, OUTPUTS_TABLES


def load_eib_with_nace():
    """Load EIB Projects and map sectors to NACE sections."""
    df = pd.read_excel(DATA_RAW / "loanExport.xlsx")
    df = df.rename(
        columns={
            "Country or Territory": "country",
            "Sector": "sector",
            "Signature Date": "signature_date",
            "Signed Amount": "signed_amount",
        }
    )
    df["signature_year"] = pd.to_datetime(df["signature_date"], dayfirst=True).dt.year
    df["signed_amount"] = (
        df["signed_amount"]
        .astype(str)
        .str.replace(r"[^0-9.,]", "", regex=True)
        .str.replace(",", "")
        .astype(float)
    )

    # Drop non-country rows and non-EU
    country_map = {
        "Austria": "AT",
        "Belgium": "BE",
        "Bulgaria": "BG",
        "Croatia": "HR",
        "Cyprus": "CY",
        "Czech Republic": "CZ",
        "Czechia": "CZ",
        "Denmark": "DK",
        "Estonia": "EE",
        "Finland": "FI",
        "France": "FR",
        "Germany": "DE",
        "Greece": "EL",
        "Hungary": "HU",
        "Ireland": "IE",
        "Italy": "IT",
        "Latvia": "LV",
        "Lithuania": "LT",
        "Luxembourg": "LU",
        "Malta": "MT",
        "Netherlands": "NL",
        "Poland": "PL",
        "Portugal": "PT",
        "Romania": "RO",
        "Slovakia": "SK",
        "Slovenia": "SI",
        "Spain": "ES",
        "Sweden": "SE",
    }
    df = df[df["country"].isin(country_map.keys())].copy()
    df["country"] = df["country"].map(country_map)

    # Load crosswalk
    cw = pd.read_csv(DATA_RAW / "eib_nace_crosswalk.csv")
    sector_to_nace = dict(zip(cw["eib_sector"], cw["nace_section"]))
    df["nace_section"] = df["sector"].map(sector_to_nace)

    # Drop unmapped sectors
    unmapped = df[df["nace_section"].isna()]["sector"].unique()
    if len(unmapped) > 0:
        print(f"Warning: {len(unmapped)} unmapped EIB sectors dropped: {unmapped}")
    df = df.dropna(subset=["nace_section"])

    return df


def build_shifts(eib_df):
    """EU-aggregate EIB signed amount by NACE section × year."""
    shifts = (
        eib_df.groupby(["nace_section", "signature_year"])["signed_amount"]
        .sum()
        .reset_index()
        .rename(columns={"signature_year": "year", "signed_amount": "eib_shift"})
    )
    return shifts


def build_shares():
    """Employment shares by NACE section × country, base year 2015."""
    sbs = pd.read_csv(DATA_RAW / "eurostat_sbs_sc_sca_r2.csv")
    sbs = sbs[sbs["indic_sb"] == "V16110"]
    sbs = sbs[sbs["time_period"] == 2015]
    # Aggregate across size classes
    emp = (
        sbs.groupby(["geo", "nace_r2"])["value"]
        .sum()
        .reset_index()
        .rename(
            columns={"geo": "country", "nace_r2": "nace_section", "value": "employment"}
        )
    )
    # Total employment per country
    total = (
        emp.groupby("country")["employment"]
        .sum()
        .reset_index()
        .rename(columns={"employment": "total_employment"})
    )
    emp = emp.merge(total, on="country", how="left")
    emp["employment_share"] = emp["employment"] / emp["total_employment"]
    return emp


def build_bartik(shares, shifts):
    """Merge shares and shifts to construct Bartik instrument."""
    # Only keep NACE sections present in both
    common_nace = set(shares["nace_section"]).intersection(set(shifts["nace_section"]))
    shares = shares[shares["nace_section"].isin(common_nace)]
    shifts = shifts[shifts["nace_section"].isin(common_nace)]

    # Cartesian product: country × year × nace_section
    countries = shares["country"].unique()
    years = shifts["year"].unique()
    naces = sorted(common_nace)

    panel = []
    for c in countries:
        for y in years:
            for n in naces:
                share = shares[
                    (shares["country"] == c) & (shares["nace_section"] == n)
                ]["employment_share"]
                shift = shifts[(shifts["nace_section"] == n) & (shifts["year"] == y)][
                    "eib_shift"
                ]
                s = share.iloc[0] if len(share) > 0 else 0
                sh = shift.iloc[0] if len(shift) > 0 else 0
                panel.append(
                    {
                        "country": c,
                        "year": y,
                        "nace_section": n,
                        "employment_share": s,
                        "eib_shift": sh,
                        "bartik_component": s * sh,
                    }
                )

    panel = pd.DataFrame(panel)
    bartik = (
        panel.groupby(["country", "year"])["bartik_component"]
        .sum()
        .reset_index()
        .rename(columns={"bartik_component": "bartik"})
    )
    return bartik, panel


def load_outcome_panel():
    """Load existing analysis panel with constraints and controls."""
    panel = pd.read_csv(DATA_PROCESSED / "eib_analysis_panel.csv")
    panel["year"] = panel["year"].astype(int)
    panel["log_gdp_pc"] = np.log(panel["gdp_per_capita"])
    panel["covid_2020"] = (panel["year"] == 2020).astype(int)
    return panel


def run_bartik_iv():
    print("=" * 70)
    print("BARTIK INSTRUMENT CONSTRUCTION AND 2SLS (Spec 3)")
    print("=" * 70)

    # Build components
    eib_df = load_eib_with_nace()
    print(f"\nEIB projects with NACE mapping: {len(eib_df)} rows")
    print(f"NACE sections: {sorted(eib_df['nace_section'].unique())}")

    shifts = build_shifts(eib_df)
    print(f"Shifts: {len(shifts)} sector-year cells")
    print(f"Years covered: {sorted(shifts['year'].unique())}")

    shares = build_shares()
    print(f"Shares: {len(shares)} country-sector cells")
    print(f"Countries with employment data: {shares['country'].nunique()}")
    print(f"Sectors with employment data: {sorted(shares['nace_section'].unique())}")

    bartik, components = build_bartik(shares, shifts)
    print(f"\nBartik instrument: {len(bartik)} country-year cells")
    print(f"Mean Bartik: {bartik['bartik'].mean():,.0f}")
    print(f"Std Bartik: {bartik['bartik'].std():,.0f}")

    # Merge with panel
    panel = load_outcome_panel()
    reg = panel.merge(bartik, on=["country", "year"], how="inner")
    print(f"\nRegression panel: {len(reg)} observations")
    print(f"Countries: {reg['country'].nunique()}")
    print(f"Years: {sorted(reg['year'].unique())}")

    # First stage
    print("\n" + "=" * 70)
    print("FIRST STAGE: EIB_per_SME ~ Bartik + controls + FE")
    print("=" * 70)

    reg["log_eib_per_sme"] = np.log(reg["eib_per_sme"])

    fs = feols(
        "log_eib_per_sme ~ bartik + log_gdp_pc + covid_2020 | country + year",
        data=reg,
        vcov={"CRV1": "country"},
    )
    print(fs.summary())

    # Get F-statistic
    # Pyfixest doesn't directly report K-P F; we approximate with t-statistic squared
    bartik_t = fs.tstat().get("bartik", np.nan)
    approx_f = bartik_t**2 if not np.isnan(bartik_t) else np.nan
    print(f"\nApproximate first-stage F (t^2): {approx_f:.2f}")
    print(f"Bartik t-statistic: {bartik_t:.3f}")

    # Get fitted values for second stage
    reg["eib_per_sme_hat"] = fs.predict(newdata=reg)

    # Second stage
    print("\n" + "=" * 70)
    print("SECOND STAGE: constraint ~ fitted(EIB_per_SME) + controls + FE")
    print("=" * 70)

    ss = feols(
        "access_to_finance_share ~ eib_per_sme_hat + log_gdp_pc + covid_2020 | country + year",
        data=reg,
        vcov={"CRV1": "country"},
    )
    print(ss.summary())

    # Also run OLS for comparison
    print("\n" + "=" * 70)
    print("OLS BASELINE: constraint ~ actual(EIB_per_SME) + controls + FE")
    print("=" * 70)

    ols = feols(
        "access_to_finance_share ~ log_eib_per_sme + log_gdp_pc + covid_2020 | country + year",
        data=reg,
        vcov={"CRV1": "country"},
    )
    print(ols.summary())

    # Save results
    results = {
        "first_stage": {
            "pi_bartik": fs.coef().get("bartik", np.nan),
            "se_bartik": fs.se().get("bartik", np.nan),
            "t_bartik": bartik_t,
            "approx_f": approx_f,
            "r2_within": getattr(fs, "_r2", np.nan),
        },
        "second_stage": {
            "beta_eib": ss.coef().get("eib_per_sme_hat", np.nan),
            "se_eib": ss.se().get("eib_per_sme_hat", np.nan),
            "t_eib": ss.tstat().get("eib_per_sme_hat", np.nan),
            "p_eib": ss.pvalue().get("eib_per_sme_hat", np.nan),
            "r2_within": getattr(ss, "_r2", np.nan),
        },
        "ols": {
            "beta_eib": ols.coef().get("log_eib_per_sme", np.nan),
            "se_eib": ols.se().get("log_eib_per_sme", np.nan),
            "t_eib": ols.tstat().get("log_eib_per_sme", np.nan),
            "p_eib": ols.pvalue().get("log_eib_per_sme", np.nan),
            "r2_within": getattr(ols, "_r2", np.nan),
        },
    }

    results_df = pd.DataFrame(results).T
    out = OUTPUTS_TABLES / "phase2b_bartik_iv.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out)
    print(f"\n{'='*70}")
    print(f"Saved results to {out}")
    print(f"{'='*70}")
    print(results_df.to_string())

    # Save instrument for potential reuse
    bartik_out = DATA_INTERIM / "bartik_instrument.csv"
    bartik.to_csv(bartik_out, index=False)
    print(f"Saved Bartik instrument to {bartik_out}")

    return reg, bartik, results


if __name__ == "__main__":
    run_bartik_iv()
