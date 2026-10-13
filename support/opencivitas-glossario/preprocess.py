#!/usr/bin/env python3
"""Scarica e unisce i metadati degli indicatori OpenCivitas per un anno.

Per ogni anno, scarica i file XLSX di metadati per tutti gli ambiti,
legge i fogli 'Indicatori', 'Determinanti' e 'Codici' e unisce in
un unico CSV.

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


# Mappa anno → prefisso funzione
YEAR_MAP = {
    2015: {"prefix": "20", "no_year": True, "suffix": "2"},
    2016: {"prefix": "30"},
    2017: {"prefix": "40"},
    2018: {"prefix": "50"},
    2019: {"prefix": "60"},
    2021: {"prefix": "70"},
    2022: {"prefix": "80"},
    2023: {"portal": True},
}

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

# 2023: XLSX diretti dal portale Liferay (no ZIP). Naming nuovo: sigle estese
# (AMMINISTR, TERR_VIAB con underscore), suffisso _01_IT. UUID: se Sogei
# ricarica un file, recuperare il nuovo URL dall'inventario catalog-watch.
PORTAL_BASE = "https://www.opencivitas.it/portale/documents/20118/0/"
PORTAL_2023 = {
    "AMMIN": "2023_Metadati_Ind_FC90_AMMINISTR_01_IT.xlsx/9e1fd560-98c5-bad0-2d77-55c8018d8a02",
    "ISTRUZ": "2023_Metadati_Ind_FC90_ISTRUZ_01_IT.xlsx/91050c02-0253-d9fb-781f-6bbca917b68a",
    "POLIZIA": "2023_Metadati_Ind_FC90_POLIZIA_01_IT.xlsx/1fe7b6fb-b7b8-5de6-ef80-cc9eae7b9729",
    "RIFIUTI": "2023_Metadati_Ind_FC90_RIFIUTI_01_IT.xlsx/85afd52b-b9a4-7d5b-465f-9b37a34b79b9",
    "SOCNID": "2023_Metadati_Ind_FC90_SOCNID_01_IT.xlsx/912e9d92-ba06-c82b-e8b5-dee94af57117",
    "TERRVIAB": "2023_Metadati_Ind_FC90_TERR_VIAB_01_IT.xlsx/6feeacb0-d373-0940-f293-91b02bb1963c",
    "TOT": "2023_Metadati_Ind_FC90_TOT_01_IT.xlsx/979ac980-1a35-ca7c-9005-1045b5aebe1e",
}


def download_and_read_metadata(url, tmp_dir, ambito_nome, year, direct_xlsx=False):
    """Scarica metadati (ZIP→XLSX o XLSX diretto) e legge i fogli.

    direct_xlsx=True (2023): la URL punta a un XLSX diretto del portale,
    niente estrazione ZIP.
    """
    xlsx_path = os.path.join(tmp_dir, "meta.xlsx")

    try:
        data = download(url, timeout=30)
    except RuntimeError:
        return []

    if direct_xlsx:
        try:
            with open(xlsx_path, "wb") as f:
                f.write(data)
        except Exception:
            return []
    else:
        zip_path = os.path.join(tmp_dir, "meta.zip")
        try:
            with open(zip_path, "wb") as f:
                f.write(data)
            with zipfile.ZipFile(zip_path) as zf:
                xlsx_files = [f for f in zf.namelist() if f.endswith(".xlsx")]
                if not xlsx_files:
                    return []
                zf.extract(xlsx_files[0], tmp_dir)
                xlsx_path = os.path.join(tmp_dir, xlsx_files[0])
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

    if year not in YEAR_MAP:
        print(f"ERRORE: anno {year} non supportato. Usa: {list(YEAR_MAP.keys())}", file=sys.stderr)
        sys.exit(1)

    is_portal = YEAR_MAP[year].get("portal", False)
    prefix = YEAR_MAP[year].get("prefix")

    with tempfile.TemporaryDirectory() as tmp_dir:
        all_rows = []
        total_downloaded = 0

        for sigla, ambito_nome in AMBITI:
            if is_portal:
                url = f"{PORTAL_BASE}{PORTAL_2023[sigla]}"
            elif YEAR_MAP[year].get("no_year"):
                suffix = YEAR_MAP[year].get("suffix", "1")
                url = f"{BASE_URL}/Metadati_Ind_FC{prefix}{sigla}_{suffix}_xlsx.zip"
            else:
                suffix = YEAR_MAP[year].get("suffix", "1")
                url = f"{BASE_URL}/{year}_Metadati_Ind_FC{prefix}{sigla}_{suffix}_xlsx.zip"
            rows = download_and_read_metadata(
                url, tmp_dir, ambito_nome, year, direct_xlsx=is_portal
            )
            if rows:
                all_rows.extend(rows)
                total_downloaded += 1
                print(f"  OK {sigla} ({ambito_nome}) — {len(rows)} voci", flush=True)
            else:
                print(f"  SKIP {sigla} ({ambito_nome})", flush=True)

        if not all_rows:
            print("ERRORE: nessun metadato scaricato", file=sys.stderr)
            sys.exit(1)

        if total_downloaded < len(AMBITI):
            print(
                f"ERRORE: solo {total_downloaded}/{len(AMBITI)} ambiti scaricati, richiesti tutti e {len(AMBITI)}",
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
