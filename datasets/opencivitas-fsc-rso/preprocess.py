#!/usr/bin/env python3
"""Scarica il CSV FSC per un anno, gestendo pattern URL diversi.

Pattern URL:
  2017-2021: https://docs.opencivitas.it/{year}_VAR_FSC_1_csv.zip
  2022-2025: https://docs.opencivitas.it/{year}_VAR_FSC_1_{year}_csv.zip

Usage: python preprocess.py <year> <output.csv>
"""

import csv
import os
import sys
import tempfile
import zipfile
from pathlib import Path

from lab_connectors.http.download import download

BASE_URL = "https://docs.opencivitas.it"

# Pattern URL per fascia anni
URL_PATTERNS = {
    range(2017, 2022): "{year}_VAR_FSC_1_csv.zip",           # 2017-2021
    range(2022, 2026): "{year}_VAR_FSC_1_{year}_csv.zip",    # 2022-2025
}


def get_url_pattern(year: int) -> str | None:
    """Restituisce il pattern URL per l'anno dato."""
    for period, pattern in URL_PATTERNS.items():
        if year in period:
            return pattern
    return None


def download_and_extract_csv(url: str, tmp_dir: str) -> str | None:
    """Scarica un file ZIP e restituisce il path del CSV estratto."""
    zip_path = os.path.join(tmp_dir, "temp.zip")
    try:
        data = download(url, timeout=60)
    except RuntimeError:
        return None
    try:
        with open(zip_path, "wb") as f:
            f.write(data)
        with zipfile.ZipFile(zip_path) as zf:
            csv_files = [f for f in zf.namelist() if f.endswith(".csv")]
            if not csv_files:
                return None
            csv_name = csv_files[0]
            zf.extract(csv_name, tmp_dir)
            return os.path.join(tmp_dir, csv_name)
    except Exception:
        return None


def main():
    if len(sys.argv) < 3:
        print("Usage: python preprocess.py <year> <output.csv>", file=sys.stderr)
        sys.exit(1)

    year = int(sys.argv[1])
    output_path = Path(sys.argv[2])

    pattern = get_url_pattern(year)
    if pattern is None:
        print(f"ERRORE: anno {year} non configurato. Supportati: 2017-2025", file=sys.stderr)
        sys.exit(1)

    url = f"{BASE_URL}/{pattern.format(year=year)}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = download_and_extract_csv(url, tmp_dir)
        if csv_path is None:
            print(f"ERRORE: download fallito per {url}", file=sys.stderr)
            sys.exit(1)

        # Leggi CSV (senza header, 3 colonne)
        rows = []
        for enc in ["utf-8-sig", "latin-1", "iso-8859-1"]:
            try:
                with open(csv_path, encoding=enc) as f:
                    reader = csv.reader(f, delimiter=";")
                    for row in reader:
                        if len(row) >= 3:
                            rows.append(row[:3])
                        elif len(row) > 0:
                            rows.append(row + [""] * (3 - len(row)))
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if not rows:
            print("ERRORE: nessuna riga letta", file=sys.stderr)
            sys.exit(1)

        # Scrivi output
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerows(rows)

        print(f"Output: {output_path} ({len(rows)} righe)", flush=True)


if __name__ == "__main__":
    main()
