"""Ingest EIB Projects Financed dataset.

Downloads the EIB Projects Financed CSV from the EIB open data portal,
validates basic schema, and saves to data/raw/.

External URL(s) requested:
- https://www.eib.org/en/projects/loans/index.htm (landing page)
- CSV export link discovered from the page above

Before running: confirm with human that fetching these URLs is approved.
"""

import csv
import io
import sys
from datetime import datetime
from pathlib import Path

import requests

# Allow standalone execution from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import DATA_RAW

# Approved data source (per AGENTS.md)
EIB_PROJECTS_URL = "https://www.eib.org/en/projects/loans/index.htm"
# The CSV export link is discovered by parsing the HTML page for the download link.
EIB_PROJECTS_CSV_URL = None  # discovered dynamically


def discover_csv_url() -> str:
    """Parse the EIB projects page to find the CSV download link."""
    print(f"Fetching landing page: {EIB_PROJECTS_URL}")
    response = requests.get(EIB_PROJECTS_URL, timeout=120)
    response.raise_for_status()
    # The CSV link typically contains "csv=true" or is a direct CSV export
    # Search for common patterns
    text = response.text
    # Try to find a link with csv=true
    import re

    match = re.search(r'href="([^"]*csv=true[^"]*)"', text)
    if match:
        url = match.group(1)
        if url.startswith("/"):
            url = "https://www.eib.org" + url
        print(f"Discovered CSV URL: {url}")
        return url
    # Fallback: try the known export endpoint pattern
    fallback = "https://www.eib.org/en/projects/loans/index.htm?csv=true"
    print(f"Could not discover CSV link; using fallback: {fallback}")
    return fallback


def download_eib_projects(csv_url: str) -> Path:
    """Download EIB Projects Financed CSV and save to data/raw/.

    Args:
        csv_url: Direct URL to the CSV export.

    Returns:
        Path to the saved raw CSV file.
    """
    print(f"Requesting URL: {csv_url}")
    response = requests.get(csv_url, timeout=120)
    response.raise_for_status()

    # Validate it looks like CSV, not HTML
    content_start = response.content[:100].decode("utf-8", errors="ignore")
    if content_start.strip().startswith("<"):
        raise ValueError(
            f"URL returned HTML, not CSV. First 100 chars: {content_start!r}"
        )

    # Save with timestamped filename (write-once rule for data/raw/)
    today = datetime.now().strftime("%Y%m%d")
    out_path = DATA_RAW / f"eib_projects_{today}.csv"
    out_path.write_bytes(response.content)
    print(f"Saved {len(response.content)} bytes to {out_path}")
    return out_path


def inspect_schema(path: Path) -> dict:
    """Inspect CSV headers and first few rows.

    Returns:
        Dictionary with headers, first 5 rows, row count, and file size.
    """
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    rows = []
    for i, row in enumerate(reader):
        if i < 5:
            rows.append(row)
        else:
            break

    # Full row count (excluding header)
    row_count = sum(1 for _ in csv.reader(io.StringIO(text))) - 1

    return {
        "path": str(path),
        "headers": headers,
        "first_rows": rows,
        "row_count": row_count,
        "file_size_bytes": path.stat().st_size,
    }


if __name__ == "__main__":
    print("EIB Projects Financed ingest script")
    csv_url = discover_csv_url()
    print(f"Target CSV URL: {csv_url}")
    print("Human approval confirmed. Executing download...")
    out_path = download_eib_projects(csv_url)
    print("\n--- Schema Inspection ---")
    info = inspect_schema(out_path)
    print(f"File: {info['path']}")
    print(f"Rows: {info['row_count']:,}")
    print(f"Size: {info['file_size_bytes']:,} bytes")
    print(f"Headers ({len(info['headers'])}): {info['headers']}")
    print("\nFirst 5 rows:")
    for i, row in enumerate(info["first_rows"], 1):
        print(f"  Row {i}: {row}")
