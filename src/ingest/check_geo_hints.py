"""Search for geographic hints in EU Countries rows."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd

from src.config import DATA_RAW


def main():
    path = DATA_RAW / "loanExport.xlsx"
    df = pd.read_excel(path, engine="openpyxl")

    cities = {
        "Paris": "France",
        "Marseille": "France",
        "Lyon": "France",
        "Berlin": "Germany",
        "Munich": "Germany",
        "Hamburg": "Germany",
        "Cologne": "Germany",
        "Madrid": "Spain",
        "Barcelona": "Spain",
        "Valencia": "Spain",
        "Rome": "Italy",
        "Milan": "Italy",
        "Turin": "Italy",
        "Naples": "Italy",
        "Warsaw": "Poland",
        "Krakow": "Poland",
        "Lisbon": "Portugal",
        "Porto": "Portugal",
        "Vienna": "Austria",
        "Athens": "Greece",
        "Brussels": "Belgium",
        "Amsterdam": "Netherlands",
        "Rotterdam": "Netherlands",
        "Dublin": "Ireland",
        "Stockholm": "Sweden",
        "Gothenburg": "Sweden",
        "Copenhagen": "Denmark",
        "Helsinki": "Finland",
        "Prague": "Czechia",
        "Budapest": "Hungary",
        "Bucharest": "Romania",
        "Sofia": "Bulgaria",
        "Zagreb": "Croatia",
        "Bratislava": "Slovakia",
        "Ljubljana": "Slovenia",
        "Tallinn": "Estonia",
        "Riga": "Latvia",
        "Vilnius": "Lithuania",
        "Luxembourg City": "Luxembourg",
        "Valletta": "Malta",
        "Nicosia": "Cyprus",
    }

    eu_generic = df[df["Country or Territory"] == "EU Countries"]
    found_cities = {}
    for city, country in cities.items():
        mask = eu_generic["Description"].str.contains(
            r"\b" + city + r"\b", case=False, na=False, regex=True
        )
        count = mask.sum()
        if count > 0:
            found_cities[country] = found_cities.get(country, 0) + count

    print("Additional cities found in descriptions:")
    for country, count in sorted(found_cities.items(), key=lambda x: -x[1]):
        print(f"  {country}: {count}")

    total_found = sum(found_cities.values())
    print(f"Total additional: {total_found} / {len(eu_generic)}")
    print(f"Combined with country names: {152 + total_found} / {len(eu_generic)}")

    # Show unidentified
    all_patterns = list(cities.keys()) + list(cities.values())
    pattern = "|".join(all_patterns)
    unidentified = eu_generic[
        ~eu_generic["Description"].str.contains(pattern, case=False, na=False)
    ]
    print(f"Unidentified rows: {len(unidentified)}")
    print("Sample unidentified rows:")
    for i, row in unidentified.head(5).iterrows():
        print(f"  Name: {row['Name']}")
        print(f"  Desc: {row['Description'][:200]}")
        print()


if __name__ == "__main__":
    main()
