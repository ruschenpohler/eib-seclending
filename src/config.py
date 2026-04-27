"""Project path configuration.

All scripts should import ROOT from this module and derive paths from it.
No hardcoded paths elsewhere.
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS_FIGURES = ROOT / "outputs" / "figures"
OUTPUTS_TABLES = ROOT / "outputs" / "tables"

# Create directories if they don't exist
for d in [DATA_RAW, DATA_INTERIM, DATA_PROCESSED, OUTPUTS_FIGURES, OUTPUTS_TABLES]:
    d.mkdir(parents=True, exist_ok=True)
