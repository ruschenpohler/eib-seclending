"""Ingest ECB SAFE aggregates via SDMX API.

Fetches financing obstacle indicators for SMEs from the ECB's SDMX API.

External URL(s) requested:
- https://data-api.ecb.europa.eu/service/data/ECB_SAFE
- https://www.ecb.europa.eu/stats/pdf/surveys/sme/ecb.safemi.en.pdf (methodology)

Before running: confirm with human that fetching these URLs is approved.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests


# Approved data source (per AGENTS.md)
ECB_SAFE_API_URL = "https://data-api.ecb.europa.eu/service/data/ECB_SAFE"
ECB_SAFE_METHODLOGY_URL = (
    "https://www.ecb.europa.eu/stats/pdf/surveys/sme/ecb.safemi.en.pdf"
)

# Series key structure for ECB SAFE:
# Dataset: ECB_SAFE
# Dimensions: typically include:
#   - REF_AREA (country)
#   - FREQ (frequency, e.g., A for annual)
#   - INDICATOR (indicator code)
#   - SIZE_CLASS (firm size class, e.g., SME)
# Common series keys may look like:
#   ECB_SAFE.A.DE.SME_FIN_OBST.SME
# But the exact key structure needs confirmation.


def discover_series_keys():
    """Query ECB SAFE data structure to discover available series keys.

    Returns:
        Response text from the dataflow query.
    """
    # First, query the dataflow definition
    dataflow_url = "https://sdw-wsrest.ecb.europa.eu/service/dataflow/ECB/ECB_SAFE"
    print(f"Requesting dataflow definition: {dataflow_url}")
    response = requests.get(
        dataflow_url,
        headers={"Accept": "application/vnd.sdmx.structure+json;version=1.0.0"},
        timeout=60,
    )
    response.raise_for_status()
    return response.text


def fetch_safe_data(series_key: str) -> str:
    """Fetch ECB SAFE data for a given series key.

    Args:
        series_key: SDMX series key string.

    Returns:
        Response text (CSV or XML).
    """
    url = f"{ECB_SAFE_API_URL}/{series_key}"
    print(f"Requesting URL: {url}")
    response = requests.get(
        url,
        headers={"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"},
        timeout=120,
    )
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    print("ECB SAFE aggregate ingest script")
    print(f"API endpoint: {ECB_SAFE_API_URL}")
    print(f"Methodology PDF: {ECB_SAFE_METHODLOGY_URL}")
    print("Awaiting human approval before executing any requests...")
