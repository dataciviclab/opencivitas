#!/usr/bin/env python3
"""Scarica e unisce i CSV indicatori OpenCivitas per un anno.

Per ogni anno, scarica i CSV degli indicatori per i 7 ambiti tematici dal
portale Liferay OpenCivitas e li unisce in un unico file con colonna
aggiuntiva 'ambito'.

Usage: python preprocess.py <year> <output.csv>
"""

import csv
import os
import sys
import tempfile
from pathlib import Path

from lab_connectors.http.download import download

# Portale Liferay OpenCivitas: CSV diretti (URL con UUID). Il vecchio dominio
# docs.opencivitas.it è dismesso. Se un run va in 404, recuperare il nuovo URL
# dall'inventario del catalog-watch (registry/catalog.json).
PORTAL_BASE = "https://www.opencivitas.it/portale/documents/20118/0/"

# anno -> {sigla ambito: "nome-file/uuid"}
PORTAL = {
    2017: {
        "AMMIN": "2017_Ind_FC40AMMIN_1/8fc4bc16-55fb-e450-6a93-f3a5b77802f8",
        "ISTRUZ": "2017_Ind_FC40ISTRUZ_1/92c0bbe3-5629-7ff4-fe12-249be90ac957",
        "POLIZIA": "2017_Ind_FC40POLIZIA_1/8b04b6a9-7a26-47c8-048f-d27107c54659",
        "RIFIUTI": "2017_Ind_FC40RIFIUTI_1/ae80db07-f9be-4f46-b9a7-97e80631a1a3",
        "SOCNID": "2017_Ind_FC40SOCNID_1/6de12fa8-a025-aa63-92f7-1af62c879b6f",
        "TERRVIAB": "2017_Ind_FC40TERRVIAB_1/95393823-c570-158c-5803-35c4a2f866c3",
        "TOT": "2017_Ind_FC40TOT_1/b77a0074-67c1-060b-ab27-e1a452538ef5",
    },
    2018: {
        "AMMIN": "2018_Ind_FC50AMMIN_1/ceca4393-4cba-d215-543e-9a970b49aede",
        "ISTRUZ": "2018_Ind_FC50ISTRUZ_1/f6110a96-17b2-a754-a14e-0e22f7168d68",
        "POLIZIA": "2018_Ind_FC50POLIZIA_1/bbc223f9-06ae-3b88-d484-3a340d0ba560",
        "RIFIUTI": "2018_Ind_FC50RIFIUTI_1/4743da5f-d9e6-362a-23ea-2492cf60127c",
        "SOCNID": "2018_Ind_FC50SOCNID_1/d16acf9f-950a-13e2-9628-2f5b453f13ab",
        "TERRVIAB": "2018_Ind_FC50TERRVIAB_1/c7a558aa-5f69-d26b-c408-7c893f2e7015",
        "TOT": "2018_Ind_FC50TOT_1/4cb9d398-12c6-93b6-2a39-2b8272bc9009",
    },
    2019: {
        "AMMIN": "2019_Ind_FC60AMMIN_1/7707054c-d67f-c28d-0d3e-26fe31ae0e14",
        "ISTRUZ": "2019_Ind_FC60ISTRUZ_1/ae4e55d0-279a-39ba-a1b3-94c1c7e58bad",
        "POLIZIA": "2019_Ind_FC60POLIZIA_1/c462e5ef-9868-240c-96fb-2b9a9d25c836",
        "RIFIUTI": "2019_Ind_FC60RIFIUTI_1/2f3ad3bd-4daf-1b87-dc84-744db0c04193",
        "SOCNID": "2019_Ind_FC60SOCNID_1/07eb2b57-3c7d-1151-9efb-9aa28c0a6aa9",
        "TERRVIAB": "2019_Ind_FC60TERRVIAB_1/e7802fa5-0156-9679-126f-53538a2ee4b9",
        "TOT": "2019_Ind_FC60TOT_2/566f11b3-3035-3b7b-8202-7fbc6796222a",
    },
    2021: {
        "AMMIN": "2021_Ind_FC70AMMIN_1/60ec9284-2ea7-9113-7be3-120d31656d48",
        "ISTRUZ": "2021_Ind_FC70ISTRUZ_1/95845cf6-8fe9-811f-715c-113af6c6da6a",
        "POLIZIA": "2021_Ind_FC70POLIZIA_1/89d71b4f-a632-19b6-4203-722371d3d36a",
        "RIFIUTI": "2021_Ind_FC70RIFIUTI_1/cd5aab36-36e3-5190-e031-70a5961815d9",
        "SOCNID": "2021_Ind_FC70SOCNID_1/1a414590-3e19-b716-1a30-205843539d6c",
        "TERRVIAB": "2021_Ind_FC70TERRVIAB_1/df67fb09-b45f-fcbd-3b0a-1f362be26ad2",
        "TOT": "2021_Ind_FC70TOT_1/753c36d9-d5c6-0dc4-3325-e335901df0ef",
    },
    2022: {
        "AMMIN": "2022_Ind_FC80AMMIN_1/a964ed19-54a8-5da2-ce31-dfd4a926d68c",
        "ISTRUZ": "2022_Ind_FC80ISTRUZ_1/6bb550ed-7786-10df-ced8-814a347c411a",
        "POLIZIA": "2022_Ind_FC80POLIZIA_1/e4a5f360-586e-dbcb-2213-de1bc5eb3bcd",
        "RIFIUTI": "2022_Ind_FC80RIFIUTI_1/b5f0c19d-53a6-5eb2-a862-46c360e38fc7",
        "SOCNID": "2022_Ind_FC80SOCNID_1/7253fba5-65ef-c16e-534b-7dabbf9b38b0",
        "TERRVIAB": "2022_Ind_FC80TERRVIAB_1/3b7454ca-e898-a4d7-6d8c-ac12cd2a6820",
        "TOT": "2022_Ind_FC80TOT_2/22645636-12c2-c12c-cd6e-0d23cd70d150",
    },
    2023: {
        "AMMIN": "2023_Ind_AMMINISTR_01_IT.csv/45e7ec1b-d282-278d-de7b-73af1b374255",
        "ISTRUZ": "2023_Ind_ISTRUZ_01_IT.csv/c9b4ea9e-d2c1-9ae4-3587-ceea43985da3",
        "POLIZIA": "2023_Ind_POLIZIA_01_IT.csv/175d849b-35f1-c439-c869-fe48959a24ce",
        "RIFIUTI": "2023_Ind_RIFIUTI_01_IT.csv/34fd224a-5cac-7676-3016-7c55fe5d6450",
        "SOCNID": "2023_Ind_SOCNID_01_IT/cfedc2c9-b05d-07cb-da97-decaf9190f5f",
        "TERRVIAB": "2023_Ind_TERR_VIAB_01_IT/5565663a-6434-27e1-1b7a-273e87b02635",
        "TOT": "2023_Ind_TOT_01_IT.csv/1086db31-bf42-8678-0520-c77eacce2a23",
    },
}

# Ambiti: sigla_nell_URL → nome_descrittivo
AMBITI = [
    ("AMMIN", "amministrazione"),
    ("ISTRUZ", "istruzione"),
    ("POLIZIA", "polizia_locale"),
    ("RIFIUTI", "rifiuti"),
    ("SOCNID", "sociale_asili_nido"),
    ("TERRVIAB", "viabilita_territorio"),
    ("TOT", "servizi_totali"),
]


def read_csv(path):
    """Legge il CSV provando UTF-8, fallback Latin-1."""
    for enc in ["utf-8-sig", "latin-1", "iso-8859-1"]:
        try:
            with open(path, encoding=enc) as f:
                return list(csv.DictReader(f, delimiter=";"))
        except (UnicodeDecodeError, UnicodeError):
            continue
    return []


def main():
    if len(sys.argv) < 3:
        print("Usage: python preprocess.py <year> <output.csv>", file=sys.stderr)
        sys.exit(1)

    year = int(sys.argv[1])
    output_path = Path(sys.argv[2])

    if year not in PORTAL:
        print(
            f"ERRORE: anno {year} non configurato. Supportati: {sorted(PORTAL.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp_dir:
        all_rows = []
        downloaded = 0

        for sigla, ambito_nome in AMBITI:
            # CSV diretto dal portale (no ZIP)
            url = f"{PORTAL_BASE}{PORTAL[year][sigla]}"
            csv_path = os.path.join(tmp_dir, f"{sigla}.csv")
            try:
                data = download(url, timeout=60)
            except RuntimeError:
                print(f"  SKIP {sigla} ({ambito_nome}) — non disponibile", flush=True)
                continue
            with open(csv_path, "wb") as f:
                f.write(data)

            rows_data = read_csv(csv_path)
            if not rows_data:
                print(f"  SKIP {sigla} — encoding non gestibile", flush=True)
                continue

            # Verifica header
            if not {"USERNAME", "Indicatore/Determinante", "Valore"}.issubset(
                set(rows_data[0].keys())
            ):
                print(f"  SKIP {sigla} — colonne inattese: {list(rows_data[0].keys())}", flush=True)
                continue

            for row in rows_data:
                username = (row.get("USERNAME") or "").strip()
                indicatore = (row.get("Indicatore/Determinante") or "").strip()
                valore_raw = (row.get("Valore") or "").strip()

                if not username or not indicatore:
                    continue

                all_rows.append(
                    {
                        "username": username,
                        "anno": str(year),
                        "ambito": ambito_nome,
                        "indicatore": indicatore,
                        "valore": valore_raw,
                    }
                )

            downloaded += 1
            print(f"  OK {sigla} ({ambito_nome}) — letto", flush=True)

        if not all_rows:
            print("ERRORE: nessun dato scaricato", file=sys.stderr)
            sys.exit(1)

        print(
            f"Scaricati {downloaded}/{len(AMBITI)} ambiti, {len(all_rows)} righe totali", flush=True
        )

        if downloaded < len(AMBITI):
            print(
                f"ERRORE: solo {downloaded}/{len(AMBITI)} ambiti scaricati, richiesti tutti e {len(AMBITI)}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Scrivi output
        fieldnames = ["username", "anno", "ambito", "indicatore", "valore"]
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(all_rows)

        print(
            f"Output: {output_path} ({len(all_rows)} righe, {output_path.stat().st_size / 1e6:.1f} MB)",
            flush=True,
        )


if __name__ == "__main__":
    main()
