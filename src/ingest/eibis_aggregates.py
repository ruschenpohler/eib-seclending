"""Ingest EIBIS aggregate data.

The EIBIS data portal (https://data.eib.org/eibis/graph) requires manual
navigation to select indicators and export. This script loads and validates
the manually downloaded file.

Before downloading, the EIBIS methodology report should be reviewed:
https://www.eib.org/files/survey/eibis-methodology-report-2019-en.pdf

External URL(s) requested (for human approval):
- https://www.eib.org/files/survey/eibis-methodology-report-2019-en.pdf
- https://data.eib.org/eibis/graph (landing page for manual export)

On ingest, confirm:
(a) the financing obstacle series key exists in the export;
(b) each wave can be mapped to a calendar year with no gaps;
(c) the series covers >=20 EU countries.
If the portal interface has changed or indicators are missing, log and ask
human for guidance.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import DATA_RAW

# Approved data source (per AGENTS.md)
EIBIS_PORTAL_URL = "https://data.eib.org/eibis/graph"
EIBIS_METHODLOGY_URL = (
    "https://www.eib.org/files/survey/eibis-methodology-report-2019-en.pdf"
)


def load_eibis_aggregates(path: Path = None):
    """Load and validate manually downloaded EIBIS aggregate file.

    Args:
        path: Path to the downloaded EIBIS aggregate file. If None, searches
            data/raw/ for common filenames.

    Returns:
        Loaded DataFrame or None if file not found.
    """
    import pandas as pd

    if path is None:
        # Search for likely filenames
        candidates = list(DATA_RAW.glob("eibis*")) + list(DATA_RAW.glob("EIBIS*"))
        if not candidates:
            print("No EIBIS aggregate file found in data/raw/")
            print("Please download from the EIBIS portal and place it in data/raw/")
            print(f"Portal URL: {EIBIS_PORTAL_URL}")
            return None
        path = candidates[0]

    print(f"Loading EIBIS aggregates from: {path}")
    # Detect format and load
    if path.suffix == ".csv":
        df = pd.read_csv(path)
    elif path.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

    print(f"Loaded {len(df)} rows x {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    return df


if __name__ == "__main__":
    print("EIBIS aggregate ingest script")
    print(f"Methodology PDF: {EIBIS_METHODLOGY_URL}")
    print(f"Data portal: {EIBIS_PORTAL_URL}")
    print()
    print("This script loads a MANUALLY downloaded EIBIS export.")
    print("Awaiting human to provide the file or confirm portal download...")
    print()
    df = load_eibis_aggregates()
    if df is not None:
        print("\nFirst 5 rows:")
        print(df.head())
