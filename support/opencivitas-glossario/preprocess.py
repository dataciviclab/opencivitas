#!/usr/bin/env python3
"""Scarica e unisce i metadati degli indicatori OpenCivitas per un anno.

Per ogni anno, scarica i file XLSX di metadati per tutti gli ambiti dal portale
Liferay OpenCivitas, legge i fogli 'Indicatori', 'Determinanti' e 'Codici' e
unisce in un unico CSV.

Usage: python preprocess.py <year> <output.csv>
"""

import csv
import os
import sys
import tempfile
from pathlib import Path

from lab_connectors.http.download import download

# Portale Liferay OpenCivitas: XLSX diretti (URL con UUID). Il vecchio dominio
# docs.opencivitas.it è dismesso. Se un run va in 404, recuperare il nuovo URL
# dall'inventario del catalog-watch (registry/catalog.json).
PORTAL_BASE = "https://www.opencivitas.it/portale/documents/20118/0/"

# anno -> {sigla ambito: "nome-file/uuid"}
PORTAL = {
    2017: {
        "AMMIN": "2017_Metadati_Ind_FC40AMMIN_1/7c2e37cf-1c34-3741-3c9a-394253f197bf",
        "ISTRUZ": "2017_Metadati_Ind_FC40ISTRUZ_1/9f6407f1-7201-09a8-ac49-8a2209b4de4d",
        "POLIZIA": "2017_Metadati_Ind_FC40POLIZIA_1/cb8bc303-c8ea-03c6-bdc4-e868ad48a721",
        "RIFIUTI": "2017_Metadati_Ind_FC40RIFIUTI_1/f61d4abd-5d05-62c2-6652-cc5d6d53f82d",
        "SOCNID": "2017_Metadati_Ind_FC40SOCNID_1/1b4c60c2-6aa7-fb15-8ff2-9c2a46200e67",
        "TERRVIAB": "2017_Metadati_Ind_FC40TERRVIAB_1/b56de9a7-b7c1-348b-a200-a6a3bf3b0ae6",
        "TOT": "2017_Metadati_Ind_FC40TOT_1/4cab917e-c680-e8d5-c190-b69f654c57a3",
    },
    2018: {
        "AMMIN": "2018_Metadati_Ind_FC50AMMIN_1/21fe323b-dcda-389f-6579-c0454e06a886",
        "ISTRUZ": "2018_Metadati_Ind_FC50ISTRUZ_1/17aa236c-ad16-6602-2ce9-0a9d0eaa6f78",
        "POLIZIA": "2018_Metadati_Ind_FC50POLIZIA_1/edf62111-02f0-27ce-8809-cc11cfb9b76a",
        "RIFIUTI": "2018_Metadati_Ind_FC50RIFIUTI_1/77eb41df-64b2-9d32-7743-0fd339c2026d",
        "SOCNID": "2018_Metadati_Ind_FC50SOCNID_1/92a144fd-3334-ef4e-cbd0-3c52a6ef5eab",
        "TERRVIAB": "2018_Metadati_Ind_FC50TERRVIAB_1/e7f1492e-ffa8-ab89-8d79-4c1e0dce2300",
        # TOT 2018 non pubblicato sul portale (vedi KNOWN_MISSING)
    },
    2019: {
        "AMMIN": "2019_Metadati_Ind_FC60AMMIN_1/776a62dd-f5f1-56b9-d2f6-d9c2ff676e6f",
        "ISTRUZ": "2019_Metadati_Ind_FC60ISTRUZ_1/a3f264d4-72c9-a5c2-ebc0-1c93bc6d38af",
        "POLIZIA": "2019_Metadati_Ind_FC60POLIZIA_1/d69c25b5-43b3-f819-7355-634d9fb0e152",
        "RIFIUTI": "2019_Metadati_Ind_FC60RIFIUTI_1/7f5132dc-903e-892a-a15f-13640f3a4f79",
        "SOCNID": "2019_Metadati_Ind_FC60SOCNID_1/b03709f1-a1d8-c59d-d6e4-726fa85a71df",
        "TERRVIAB": "2019_Metadati_Ind_FC60TERRVIAB_1/4aecb07f-f3c3-3589-eda9-fb519573096e",
        "TOT": "2019_Metadati_Ind_FC60TOT_2/3bcc08fe-b12a-89b9-c562-f623012ce263",
    },
    2021: {
        "AMMIN": "2021_Metadati_Ind_FC70AMMIN_1/535e9b0c-e6e7-90e3-41aa-410ff4882100",
        "ISTRUZ": "2021_Metadati_Ind_FC70ISTRUZ_1/20137e0a-e661-788b-26d4-77dfea52e711",
        "POLIZIA": "2021_Metadati_Ind_FC70POLIZIA_1/8445504c-28b3-99a3-40ba-0cb2bfd40633",
        "RIFIUTI": "2021_Metadati_Ind_FC70RIFIUTI_1/44a87d56-85f0-5892-6ebb-da5315ac0404",
        "SOCNID": "2021_Metadati_Ind_FC70SOCNID_1/bcf24867-6c3a-d78e-2ba9-ef0e0d9e1b67",
        "TERRVIAB": "2021_Metadati_Ind_FC70TERRVIAB_1/0d9c8402-3f90-8639-a60b-56f09ab7c2f1",
        "TOT": "2021_Metadati_Ind_FC70TOT_1/4f13ca9b-ea7f-cc03-1d8b-1eeaf725a948",
    },
    2022: {
        "AMMIN": "2022_Metadati_Ind_FC80AMMIN_1/56e6da9e-7f96-b853-333b-4d6e95aeba40",
        "ISTRUZ": "2022_Metadati_Ind_FC80ISTRUZ_1/4f41d7bd-37bc-4683-dd86-52823ee8bef2",
        "POLIZIA": "2022_Metadati_Ind_FC80POLIZIA_1/99fa2689-b946-11a0-03c5-afb09d8f29b9",
        "RIFIUTI": "2022_Metadati_Ind_FC80RIFIUTI_1/656efe94-0367-0fe3-749a-9f6d73f5918a",
        "SOCNID": "2022_Metadati_Ind_FC80SOCNID_1/cd9ee08a-7a6b-b649-9fdd-321fd951a48a",
        "TERRVIAB": "2022_Metadati_Ind_FC80TERRVIAB_1/ec4634e5-7124-148b-10eb-101576283647",
        "TOT": "2022_Metadati_Ind_FC80TOT_1/a1392bd6-090b-a650-d3f8-f0383869298e",
    },
    2023: {
        "AMMIN": "2023_Metadati_Ind_FC90_AMMINISTR_01_IT.xlsx/9e1fd560-98c5-bad0-2d77-55c8018d8a02",
        "ISTRUZ": "2023_Metadati_Ind_FC90_ISTRUZ_01_IT.xlsx/91050c02-0253-d9fb-781f-6bbca917b68a",
        "POLIZIA": "2023_Metadati_Ind_FC90_POLIZIA_01_IT.xlsx/1fe7b6fb-b7b8-5de6-ef80-cc9eae7b9729",
        "RIFIUTI": "2023_Metadati_Ind_FC90_RIFIUTI_01_IT.xlsx/85afd52b-b9a4-7d5b-465f-9b37a34b79b9",
        "SOCNID": "2023_Metadati_Ind_FC90_SOCNID_01_IT.xlsx/912e9d92-ba06-c82b-e8b5-dee94af57117",
        "TERRVIAB": "2023_Metadati_Ind_FC90_TERR_VIAB_01_IT.xlsx/6feeacb0-d373-0940-f293-91b02bb1963c",
        "TOT": "2023_Metadati_Ind_FC90_TOT_01_IT.xlsx/979ac980-1a35-ca7c-9005-1045b5aebe1e",
    },
}

# Ambiti mancanti nella fonte: (anno, sigla). Non è un errore, il file non è
# pubblicato dal portale. 2018 TOT metadati: assente su portale e Wayback
# (verificato 2026-11-05) — si perdono le voci servizi_totali del 2018.
KNOWN_MISSING = {(2018, "TOT")}

# Ambiti
AMBITI = [
    ("AMMIN", "amministrazione"),
    ("ISTRUZ", "istruzione"),
    ("POLIZIA", "polizia_locale"),
    ("RIFIUTI", "rifiuti"),
    ("SOCNID", "sociale_asili_nido"),
    ("TERRVIAB", "viabilita_territorio"),
    ("TOT", "servizi_totali"),
]


def download_and_read_metadata(url, tmp_dir, ambito_nome, year):
    """Scarica un XLSX diretto dal portale e legge i fogli Indicatori/Determinanti/Codici."""
    xlsx_path = os.path.join(tmp_dir, "meta.xlsx")

    try:
        data = download(url, timeout=30)
    except RuntimeError:
        return []

    try:
        with open(xlsx_path, "wb") as f:
            f.write(data)
    except Exception:
        return []

    # Leggi fogli Indicatori, Determinanti, Codici con pandas
    try:
        import pandas as pd

        xls = pd.ExcelFile(xlsx_path)
        rows = []

        # 2023: colonne in italiano; anni precedenti: prefisso VAR_*
        def _pick(df, *candidates):
            for c in candidates:
                if c in df.columns:
                    return c
            return None

        # Foglio 1: Indicatori
        sheet_ind = None
        for s in xls.sheet_names:
            if s.upper().startswith("INDICATORI"):
                sheet_ind = s
                break
        if sheet_ind:
            df = pd.read_excel(xls, sheet_name=sheet_ind)
            cod_col = _pick(df, "VAR_IND_COD", "Codice Indicatore")
            des_col = _pick(df, "VAR_IND_DES", "Descrizione")
            if cod_col and des_col:
                for _, r in df.iterrows():
                    codice = str(r.get(cod_col, "")).strip()
                    desc = str(r.get(des_col, "")).strip()
                    if codice and desc and codice != "nan":
                        rows.append(
                            {
                                "codice_indicatore": codice,
                                "descrizione": desc,
                                "tipo": "IND",
                                "categoria": str(
                                    r.get(_pick(df, "VAR_IND_TIP", "Tipo di indicatore") or "", "")
                                ).strip(),
                                "funzione": str(
                                    r.get(_pick(df, "VAR_IND_FUNZIONE", "Funzione") or "", "")
                                ).strip(),
                                "ordine": str(
                                    r.get(_pick(df, "VAR_IND_ORD", "Var Ord") or "", "")
                                ).strip(),
                                "anno": str(year),
                                "ambito": ambito_nome,
                            }
                        )

        # Foglio 2: Determinanti — 2023 usa il prefisso abbreviato "Det_"
        sheet_det = None
        for s in xls.sheet_names:
            su = s.upper()
            if su.startswith("DETERMINANTI") or su.startswith("DET_"):
                sheet_det = s
                break
        if sheet_det:
            df = pd.read_excel(xls, sheet_name=sheet_det)
            cod_col = _pick(df, "VAR_DET_COD", "Codice Determinante")
            des_col = _pick(df, "VAR_DET_DES", "Descrizione")
            if cod_col and des_col:
                for _, r in df.iterrows():
                    codice = str(r.get(cod_col, "")).strip()
                    desc = str(r.get(des_col, "")).strip()
                    if codice and desc and codice != "nan":
                        rows.append(
                            {
                                "codice_indicatore": codice,
                                "descrizione": desc,
                                "tipo": "DET",
                                "categoria": str(
                                    r.get(_pick(df, "VAR_DET_CAT_DES", "Categoria") or "", "")
                                ).strip(),
                                "funzione": str(
                                    r.get(_pick(df, "VAR_DET_FUNZIONE", "Funzione") or "", "")
                                ).strip(),
                                "ordine": "",
                                "anno": str(year),
                                "ambito": ambito_nome,
                            }
                        )

        # Foglio 3: Codici anomalia (identico tra anni)
        sheet_cod = None
        for s in xls.sheet_names:
            if s.upper().startswith("CODICI"):
                sheet_cod = s
                break
        if sheet_cod:
            df = pd.read_excel(xls, sheet_name=sheet_cod)
            col_map = {c.upper().replace(" ", "_"): c for c in df.columns}
            cod_col = col_map.get("CODICE", "")
            des_col = col_map.get("DESCRIZIONE_CODICE", "")
            fun_col = col_map.get("FUNZIONE", "")
            if cod_col and des_col:
                for _, r in df.iterrows():
                    codice = str(r.get(cod_col, "")).strip()
                    desc = str(r.get(des_col, "")).strip()
                    if codice and desc and codice != "nan":
                        rows.append(
                            {
                                "codice_indicatore": codice,
                                "descrizione": desc,
                                "tipo": "COD",
                                "categoria": "",
                                "funzione": str(r.get(fun_col, "")).strip(),
                                "ordine": "",
                                "anno": str(year),
                                "ambito": ambito_nome,
                            }
                        )

        return rows
    except ImportError:
        print("ERRORE: pandas non installato", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"  ERRORE lettura XLSX: {e}", file=sys.stderr)
        return []


def main():
    if len(sys.argv) < 3:
        print("Usage: python preprocess.py <year> <output.csv>", file=sys.stderr)
        sys.exit(1)

    year = int(sys.argv[1])
    output_path = Path(sys.argv[2])

    if year not in PORTAL:
        print(f"ERRORE: anno {year} non supportato. Usa: {sorted(PORTAL.keys())}", file=sys.stderr)
        sys.exit(1)

    expected = len(AMBITI) - sum(1 for (y, _s) in KNOWN_MISSING if y == year)

    with tempfile.TemporaryDirectory() as tmp_dir:
        all_rows = []
        total_downloaded = 0

        for sigla, ambito_nome in AMBITI:
            if (year, sigla) in KNOWN_MISSING:
                print(f"  SKIP {sigla} ({ambito_nome}) — non pubblicato dalla fonte", flush=True)
                continue

            url = f"{PORTAL_BASE}{PORTAL[year][sigla]}"
            rows = download_and_read_metadata(url, tmp_dir, ambito_nome, year)
            if rows:
                all_rows.extend(rows)
                total_downloaded += 1
                print(f"  OK {sigla} ({ambito_nome}) — {len(rows)} voci", flush=True)
            else:
                print(f"  SKIP {sigla} ({ambito_nome})", flush=True)

        if not all_rows:
            print("ERRORE: nessun metadato scaricato", file=sys.stderr)
            sys.exit(1)

        if total_downloaded < expected:
            print(
                f"ERRORE: solo {total_downloaded}/{expected} ambiti scaricati, richiesti tutti e {expected}",
                file=sys.stderr,
            )
            sys.exit(1)

        fieldnames = [
            "codice_indicatore",
            "descrizione",
            "tipo",
            "categoria",
            "funzione",
            "ordine",
            "anno",
            "ambito",
        ]
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(all_rows)

        print(f"Output: {output_path} ({len(all_rows)} righe)", flush=True)


if __name__ == "__main__":
    main()
