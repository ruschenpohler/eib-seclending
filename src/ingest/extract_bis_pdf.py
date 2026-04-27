"""Extract methodology and geographic info from BIS working paper PDF."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pdfplumber


def main():
    pdf_path = Path("data/raw/bis_work1006.pdf")
    if not pdf_path.exists():
        print(f"PDF not found at {pdf_path}")
        return

    out_path = pdf_path.with_suffix(".txt")
    with pdfplumber.open(pdf_path) as pdf, open(out_path, "w", encoding="utf-8") as out:
        out.write(f"Total pages: {len(pdf.pages)}\n\n")
        # Search first 30 pages for methodology/data sections
        for i in range(min(30, len(pdf.pages))):
            text = pdf.pages[i].extract_text()
            if text and any(
                kw in text.lower()
                for kw in [
                    "data",
                    "sample",
                    "geograph",
                    "region",
                    "nuts",
                    "country",
                    "orbis",
                    "firm",
                    "address",
                ]
            ):
                out.write(f"=== Page {i+1} ===\n")
                out.write(text[:2000])
                out.write("\n\n")
    print(f"Extracted text saved to {out_path}")


if __name__ == "__main__":
    main()
