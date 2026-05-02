"""Holm-adjusted p-values for targeting and heterogeneity families.

Targeting family (k=5):
  - Contemporaneous within-country (primary)
  - Lagged within-country (primary)
  - Between-country (exploratory)
  - Mundlak beta_W (exploratory)
  - Mundlak beta_B (exploratory)

Heterogeneity family (k=6):
  - Euro area subsample
  - Non-euro subsample
  - Euro interaction
  - High constraint subsample
  - Low constraint subsample
  - High constraint interaction

Holm procedure: order p-values ascending, compare each to alpha/(k-i+1).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd

from src.config import OUTPUTS_TABLES


def holm_adjust(pvals, alpha=0.05):
    """Compute Holm-adjusted p-values and rejection decisions.

    Returns DataFrame with columns: idx, raw_p, rank, threshold, reject, holm_p
    """
    k = len(pvals)
    df = pd.DataFrame({"idx": range(k), "raw_p": pvals})
    df = df.sort_values("raw_p").reset_index(drop=True)
    df["rank"] = range(1, k + 1)
    df["threshold"] = alpha / (k - df["rank"] + 1)

    # Sequential rejection
    df["reject"] = df["raw_p"] <= df["threshold"]
    # Find first failure
    fail_idx = df[~df["reject"]].index
    if len(fail_idx) > 0:
        first_fail = fail_idx[0]
        df.loc[first_fail:, "reject"] = False

    # Adjusted p-values: max over j<=i of (k-j+1)*p_(j)
    df["holm_p"] = 0.0
    for i in range(k):
        df.loc[i, "holm_p"] = np.max((k - df.loc[:i, "rank"] + 1) * df.loc[:i, "raw_p"])
    df["holm_p"] = np.minimum(df["holm_p"], 1.0)

    # Sort back to original order
    df = df.sort_values("idx").reset_index(drop=True)
    return df


def main():
    print("=" * 60)
    print("HOLM-ADJUSTED P-VALUES")
    print("=" * 60)

    # Targeting family
    print("\n--- Targeting family (k=5) ---")
    targeting_names = [
        "Contemporaneous (within)",
        "Lagged t-1 (within)",
        "Between-country",
        "Mundlak beta_W",
        "Mundlak beta_B",
    ]
    targeting_pvals = np.array([0.328, 0.901, 0.0087, 0.109, 0.0003])
    df_t = holm_adjust(targeting_pvals)
    df_t["test"] = targeting_names

    print(f"{'Test':<30} {'Raw p':>10} {'Holm p':>10} {'Reject?':>8}")
    print("-" * 60)
    for _, row in df_t.iterrows():
        print(
            f"{row['test']:<30} {row['raw_p']:>10.4f} {row['holm_p']:>10.4f}"
            f" {('Yes' if row['reject'] else 'No'):>8}"
        )

    # Heterogeneity family
    print("\n--- Heterogeneity family (k=6) ---")
    hetero_names = [
        "Euro area",
        "Non-euro",
        "Euro interaction",
        "High constraint",
        "Low constraint",
        "High interaction",
    ]
    hetero_pvals = np.array([0.543, 0.153, 0.221, 0.215, 0.510, 0.791])
    df_h = holm_adjust(hetero_pvals)
    df_h["test"] = hetero_names

    print(f"{'Test':<30} {'Raw p':>10} {'Holm p':>10} {'Reject?':>8}")
    print("-" * 60)
    for _, row in df_h.iterrows():
        print(
            f"{row['test']:<30} {row['raw_p']:>10.4f} {row['holm_p']:>10.4f}"
            f" {('Yes' if row['reject'] else 'No'):>8}"
        )

    # Save
    df_t["family"] = "targeting"
    df_h["family"] = "heterogeneity"
    combined = pd.concat([df_t, df_h], ignore_index=True)
    out = OUTPUTS_TABLES / "phase1_holm_adjustment.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    combined[["family", "test", "raw_p", "holm_p", "reject"]].to_csv(out, index=False)
    print(f"\nSaved to {out}")

    return combined


if __name__ == "__main__":
    main()
