"""Descriptive outputs — Beats 1, 2, 3 for Phase 1.

Beat 1: Constraint map — choropleth of mean access-to-finance share by country
Beat 2: Scatter — annual change in constraint vs. change in EIB volume per SME
Beat 3: Time series — EIB intensity and constraints over time

Beat 4 (cohesion distribution) is deferred — Check 6 not yet completed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

from src.config import DATA_PROCESSED, OUTPUTS_FIGURES


def load_panel():
    df = pd.read_csv(DATA_PROCESSED / "eib_analysis_panel.csv")
    df["year"] = df["year"].astype(int)
    return df


def beat1_constraint_map(panel):
    """Choropleth map of mean access-to-finance constraint share by country."""
    print("\n=== Beat 1: Constraint Map ===")

    # Mean constraint by country (2015-2021)
    mean_constraint = (
        panel.groupby("country")["access_to_finance_share"].mean().reset_index()
    )
    mean_constraint.columns = ["iso_a2", "constraint_share"]

    # Load world shapefile and filter for Europe
    world_url = (
        "https://naciscdn.org/naturalearth/110m/cultural/"
        "ne_110m_admin_0_countries.zip"
    )
    world = gpd.read_file(world_url)

    # Fix Natural Earth's broken ISO_A2 codes before any merge
    # France is coded as -99; patch it by name
    world.loc[world["NAME"] == "France", "ISO_A2"] = "FR"
    # Greece is already GR; EL is our data code, mapped below

    europe = world[world["CONTINENT"] == "Europe"].copy()
    europe = pd.concat(
        [europe, world[world["ISO_A2"].isin(["CY", "TR"])]]
    ).drop_duplicates(subset=["ISO_A2"])
    europe = europe.rename(columns={"ISO_A2": "ne_iso"})

    # Map our data codes to Natural Earth codes
    iso_map = {"EL": "GR"}
    mean_constraint["ne_iso"] = mean_constraint["iso_a2"].replace(iso_map)

    # Merge
    europe = europe.merge(mean_constraint, on="ne_iso", how="left")

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    # Plot countries with data
    europe_with_data = europe[europe["constraint_share"].notna()]
    europe_with_data.plot(
        column="constraint_share",
        cmap="YlOrRd",
        linewidth=0.5,
        ax=ax,
        edgecolor="0.5",
        legend=True,
        legend_kwds={
            "label": "Share of SMEs reporting access to finance as main obstacle",
            "orientation": "horizontal",
            "pad": 0.03,
            "shrink": 0.6,
        },
    )

    # Plot countries with no data in thin black outlines
    europe_no_data = europe[europe["constraint_share"].isna()]
    if not europe_no_data.empty:
        europe_no_data.plot(
            ax=ax,
            facecolor="none",
            edgecolor="black",
            linewidth=0.3,
        )

    ax.set_title(
        "Financial Constraints by Country (2015-2021 mean)\n"
        "EC SAFE Survey: Share of SMEs ranking access to finance as most important problem",
        fontsize=11,
    )
    ax.set_axis_off()

    out = OUTPUTS_FIGURES / "constraint_map.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


def beat2_delta_scatter(panel):
    """Scatter: annual change in constraint vs. annual change in EIB per SME."""
    print("\n=== Beat 2: Delta Scatter ===")

    panel = panel.sort_values(["country", "year"])
    panel["d_constraint"] = panel.groupby("country")["access_to_finance_share"].diff()
    panel["d_eib_per_sme"] = panel.groupby("country")["eib_per_sme"].diff()

    # Drop NaNs from first-differencing
    df = panel.dropna(subset=["d_constraint", "d_eib_per_sme"]).copy()

    fig, ax = plt.subplots(figsize=(9, 7))

    # Scatter with country labels for outliers
    ax.scatter(
        df["d_eib_per_sme"],
        df["d_constraint"],
        alpha=0.6,
        s=60,
        edgecolors="k",
        linewidths=0.3,
    )

    # Label points with largest absolute residuals from OLS fit
    # (these are the true outliers: they violate the correlation pattern most strongly)
    z = np.polyfit(df["d_eib_per_sme"], df["d_constraint"], 1)
    p = np.poly1d(z)
    df["residual"] = df["d_constraint"] - p(df["d_eib_per_sme"])
    top_residuals = df.nlargest(8, "residual")
    bottom_residuals = df.nsmallest(8, "residual")
    outliers = pd.concat([top_residuals, bottom_residuals]).drop_duplicates()

    # Also label extreme corners: minimum EIB funding and minimum constraint
    # These may not have extreme residuals but are visually informative
    min_eib = df.loc[df["d_eib_per_sme"].idxmin()]
    min_constraint = df.loc[df["d_constraint"].idxmin()]
    extreme_corners = pd.DataFrame([min_eib, min_constraint])
    outliers = pd.concat([outliers, extreme_corners]).drop_duplicates()

    for _, row in outliers.iterrows():
        ax.annotate(
            f"{row['country']} {int(row['year'])}",
            (row["d_eib_per_sme"], row["d_constraint"]),
            fontsize=7,
            alpha=0.8,
        )

    # OLS fit line
    z = np.polyfit(df["d_eib_per_sme"], df["d_constraint"], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df["d_eib_per_sme"].min(), df["d_eib_per_sme"].max(), 100)
    ax.plot(
        x_line, p(x_line), "r--", linewidth=1.5, label=f"OLS fit (slope={z[0]:.2e})"
    )

    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.set_xlabel("Δ EIB signed amount per SME (EUR, year-on-year)", fontsize=10)
    ax.set_ylabel(
        "Δ Share of SMEs reporting access to finance as main obstacle (pp, year-on-year)",
        fontsize=10,
    )
    ax.set_title(
        "Annual Changes: EIB Lending Intensity vs. Financial Constraints\n"
        f"{len(df)} country-year observations, 2016-2021",
        fontsize=11,
    )
    ax.legend(loc="upper right")

    out = OUTPUTS_FIGURES / "delta_scatter.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")

    # Print correlation
    corr = df["d_eib_per_sme"].corr(df["d_constraint"])
    print(f"Correlation (Delta EIB vs Delta Constraint): {corr:.3f}")


def beat3_time_series(panel):
    """Time series of mean EIB intensity and mean constraint over time."""
    print("\n=== Beat 3: Time Series ===")

    ts = (
        panel.groupby("year")
        .agg(
            mean_eib_per_sme=("eib_per_sme", "mean"),
            median_eib_per_sme=("eib_per_sme", "median"),
            mean_constraint=("access_to_finance_share", "mean"),
            median_constraint=("access_to_finance_share", "median"),
        )
        .reset_index()
    )

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color1 = "tab:blue"
    ax1.set_xlabel("Year", fontsize=10)
    ax1.set_ylabel("Mean EIB signed amount per SME (EUR)", color=color1, fontsize=10)
    ax1.plot(
        ts["year"],
        ts["mean_eib_per_sme"],
        color=color1,
        marker="o",
        linewidth=2,
        label="Mean EIB/SME",
    )
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(0, ts["mean_eib_per_sme"].max() * 1.2)

    ax2 = ax1.twinx()
    color2 = "tab:red"
    ax2.set_ylabel(
        "Mean share reporting access to finance as main obstacle",
        color=color2,
        fontsize=10,
    )
    ax2.plot(
        ts["year"],
        ts["mean_constraint"],
        color=color2,
        marker="s",
        linewidth=2,
        linestyle="--",
        label="Mean constraint share",
    )
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(0, ts["mean_constraint"].max() * 1.5)

    fig.suptitle(
        "EIB Lending Intensity and Financial Constraints Over Time\n"
        "EU-27 averages, 2015-2021",
        fontsize=11,
    )

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    out = OUTPUTS_FIGURES / "timeseries.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")

    # Also save a country-facet version for selected countries
    selected = ["DE", "FR", "IT", "ES", "PL", "RO", "NL", "AT"]
    facet_df = panel[panel["country"].isin(selected)].copy()

    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharex=True, sharey="row")
    axes = axes.flatten()

    for idx, country in enumerate(selected):
        ax = axes[idx]
        cdf = facet_df[facet_df["country"] == country].sort_values("year")

        ax2 = ax.twinx()
        (line1,) = ax.plot(
            cdf["year"],
            cdf["eib_per_sme"] / 1000,
            color="tab:blue",
            marker="o",
            linewidth=1.5,
            label="EIB/SME (kEUR)",
        )
        (line2,) = ax2.plot(
            cdf["year"],
            cdf["access_to_finance_share"] * 100,
            color="tab:red",
            marker="s",
            linewidth=1.5,
            linestyle="--",
            label="Constraint (%)",
        )

        ax.set_title(country, fontsize=10)
        ax.set_xlabel("")
        if idx % 4 == 0:
            ax.set_ylabel("EIB/SME (kEUR)", color="tab:blue", fontsize=8)
        if idx % 4 == 3:
            ax2.set_ylabel("Constraint (%)", color="tab:red", fontsize=8)

        # Add legend to the first subplot only
        if idx == 0:
            ax.legend(
                handles=[line1, line2],
                labels=["EIB/SME (kEUR)", "Constraint (%)"],
                loc="upper left",
                fontsize=7,
            )

    fig.suptitle(
        "EIB Intensity and Financial Constraints by Country (selected EU-27)",
        fontsize=12,
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    out2 = OUTPUTS_FIGURES / "timeseries_byCountry.png"
    fig.savefig(out2, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out2}")


if __name__ == "__main__":
    panel = load_panel()
    beat1_constraint_map(panel)
    beat2_delta_scatter(panel)
    beat3_time_series(panel)
    print("\nAll descriptive beats generated.")
