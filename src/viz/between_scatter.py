"""Between-country scatter figure.

Scatter of country-mean log EIB intensity vs country-mean constraint share,
with regression line, 95% CI band, and country labels.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

from src.config import DATA_PROCESSED, OUTPUTS_FIGURES


def create_between_scatter():
    """Create between-country scatter plot."""
    print("Creating between-country scatter...")

    panel = pd.read_csv(DATA_PROCESSED / "eib_analysis_panel.csv")
    panel = panel.dropna(
        subset=["eib_per_sme", "access_to_finance_share", "gdp_per_capita", "country"]
    )

    # Collapse to country means
    country_means = (
        panel.groupby("country")
        .agg(
            constraint_mean=("access_to_finance_share", "mean"),
            eib_per_sme_mean=("eib_per_sme", "mean"),
            gdp_pc_mean=("gdp_per_capita", "mean"),
        )
        .reset_index()
    )
    country_means["log_eib_per_sme"] = np.log(country_means["eib_per_sme_mean"])
    country_means["log_gdp_pc"] = np.log(country_means["gdp_pc_mean"])

    # Regression for line and CI
    X = sm.add_constant(country_means["constraint_mean"])
    y = country_means["log_eib_per_sme"]
    model = sm.OLS(y, X)
    fit = model.fit(cov_type="HC3")

    beta = fit.params["constraint_mean"]
    pval = fit.pvalues["constraint_mean"]

    # Predict for plotting
    x_range = np.linspace(
        country_means["constraint_mean"].min() - 0.01,
        country_means["constraint_mean"].max() + 0.01,
        100,
    )
    X_pred = sm.add_constant(x_range)
    pred = fit.get_prediction(X_pred)
    pred_mean = pred.predicted_mean
    pred_ci = pred.conf_int()

    # Plot
    fig, ax = plt.subplots(figsize=(10, 7))

    # Scatter points
    ax.scatter(
        country_means["constraint_mean"],
        country_means["log_eib_per_sme"],
        s=80,
        alpha=0.7,
        edgecolors="black",
        linewidth=0.5,
        zorder=3,
    )

    # Country labels
    for _, row in country_means.iterrows():
        ax.annotate(
            row["country"],
            (row["constraint_mean"], row["log_eib_per_sme"]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
            alpha=0.8,
        )

    # Regression line
    ax.plot(x_range, pred_mean, color="darkred", linewidth=2, zorder=2)

    # 95% CI band
    ax.fill_between(
        x_range,
        pred_ci[:, 0],
        pred_ci[:, 1],
        alpha=0.2,
        color="darkred",
        zorder=1,
    )

    # Annotation
    ax.text(
        0.05,
        0.95,
        f"beta = {beta:+.2f}\np = {pval:.3f}\nN = {len(country_means)}",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    ax.set_xlabel("Mean financing constraint share (2015-2021)", fontsize=11)
    ax.set_ylabel("Mean log EIB lending per SME (2015-2021)", fontsize=11)
    ax.set_title(
        "Between-country targeting: EIB intensity vs financing constraints",
        fontsize=12,
    )

    sns.despine()
    plt.tight_layout()

    out = OUTPUTS_FIGURES / "between_scatter.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Saved to {out}")
    plt.close()

    return country_means


if __name__ == "__main__":
    create_between_scatter()
