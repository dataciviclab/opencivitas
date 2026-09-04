#!/usr/bin/env python3
"""Scarica il RDF TOT OpenCivitas per un anno e converte in CSV wide.

Pattern URL:
  2015: https://docs.opencivitas.it/2015_FC20TOT_2_rdf.zip
  2016-2022: https://docs.opencivitas.it/{year}_FC{prefix}TOT_{suffix}_rdf.zip

Il file RDF e' XML con elementi <vi:rig> che hanno attributi = colonne wide.
Le colonne variano tra anni. Questo script le normalizza in nomi canonici.
Output: CSV wide con ; come delimitatore.

Usage: python preprocess.py <year> <output.csv>
"""

import csv
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from lab_connectors.http.download import download

BASE_URL = "https://docs.opencivitas.it"

# Mappa anno -> (prefix, suffix) per URL pattern RDF TOT
YEAR_MAP = {
    2015: ("20", "2"),
    2016: ("30", "1"),
    2017: ("40", "1"),
    2018: ("50", "1"),
    2019: ("60", "1"),
    2021: ("70", "1"),
    2022: ("80", "1"),
}

# Colonne da escludere (junk / empty in alcuni anni)
EXCLUDE_COLS = {"ccc", "cic", "cd", "pic", "pd", "ric", "rd"}

# Normalizzazione nomi colonne: anno-specifico -> nome canonico
# Le colonne variano tra anni (metodologia cambia), ma il significato e' lo stesso.
COL_RENAME = {
    # Spesa standard / performance (stabili)
    "FST_RIPROPORZIONATO_BI": "FST_RIPROPORZIONATO_BI",
    "FST_RIPROPORZIONATO_BI_PROAB": "FST_RIPROPORZIONATO_BI_PROAB",
    "SPESA_STORICA": "SPESA_STORICA",
    "SPESA_STORICA_PROAB": "SPESA_STORICA_PROAB",
    "POSIZIONE_OUTPUT_PERC_TOT": "POSIZIONE_OUTPUT_PERC_TOT",
    "POSIZIONE_SPESA_PERC_TOT": "POSIZIONE_SPESA_PERC_TOT",
    "COORD_OUT": "COORD_OUT",
    "COORD_SPESA": "COORD_SPESA",
    "COSTO_LAVORO_PROAB": "COSTO_LAVORO_PROAB",
    "DIFF_OUT_PERC_TOT": "DIFF_OUT_PERC_TOT",
    "DESCR_NON_VALUTABILE_OUT_TOT": "DESCR_NON_VALUTABILE_OUT_TOT",
    "DESCR_NON_VALUTABILE_SPESA_TOT": "DESCR_NON_VALUTABILE_SPESA_TOT",
    "SERV_NO_VALUT_OUT_TOT": "SERV_NO_VALUT_OUT_TOT",
    "SERV_NO_VALUT_SPESA_TOT": "SERV_NO_VALUT_SPESA_TOT",
    "FL_DIF_OUTPUT_MAG_0": "FL_DIF_OUTPUT_MAG_0",
    "FL_DIF_OUTPUT_MIN_0": "FL_DIF_OUTPUT_MIN_0",
    "FL_DIF_SPESA_MAG_0": "FL_DIF_SPESA_MAG_0",
    "FL_DIF_SPESA_MIN_0": "FL_DIF_SPESA_MIN_0",
    "FL_NO_CONFRONTO_OUT": "FL_NO_CONFRONTO_OUT",
    "FL_NO_CONFRONTO_SPESA": "FL_NO_CONFRONTO_SPESA",
    "FL_NO_VALUTABILE": "FL_NO_VALUTABILE",
    "FL_SPESA_MENO_OUT_MENO": "FL_SPESA_MENO_OUT_MENO",
    "FL_SPESA_MENO_OUT_PIU": "FL_SPESA_MENO_OUT_PIU",
    "FL_SPESA_PIU_OUT_MENO": "FL_SPESA_PIU_OUT_MENO",
    "FL_SPESA_PIU_OUT_PIU": "FL_SPESA_PIU_OUT_PIU",
    # Dipendenti (cambia nome tra anni)
    "DIPENDENTI_X1000AB": "DIPENDENTI_X1000AB",
    "F_ADDETTI_I_2015_P": "DIPENDENTI_X1000AB",
    "F_ADDETTI_I_2016_P": "DIPENDENTI_X1000AB",
    "F_ADDETTI_I_2017_P": "DIPENDENTI_X1000AB",
    "F_ADDETTI_I_2018_P": "DIPENDENTI_X1000AB",
    "F_ADDETTI_I_2019_P": "DIPENDENTI_X1000AB",
    "F_ADDETTI_I_P_MEAN": "DIPENDENTI_X1000AB",
    # Determinanti demografiche
    "F_POP_C": "F_POP_C",
    "F_DENSITA_MEAN": "F_DENSITA_MEAN",
    "F_INCID_OLTRE_75_MEAN": "F_INCID_OLTRE_75_MEAN",
    "F_INCID_POP_STRA_MEAN": "F_INCID_POP_STRA_MEAN",
    "F_INCID_15_64_MEAN": "F_INCID_15_64_MEAN",
    "F_INCID_65_74_MEAN": "F_INCID_65_74_MEAN",
    "F_DEPRIVAZIONE_MEAN": "F_DEPRIVAZIONE_MEAN",
    "F_DIFF_PENDOLARI_N_P": "F_DIFF_PENDOLARI_N_P",
    "F_IMMOBILI_TOTALI_P": "F_IMMOBILI_TOTALI_P",
    "F_CONTESTO": "F_CONTESTO",
    # Altre determinanti (tenute come sono)
    "F_ABIT_DISP_MEAN_C": "F_ABIT_DISP_MEAN_C",
    "F_ABIT_LOC_E_ALTRI_UTIL_MEAN_C": "F_ABIT_LOC_E_ALTRI_UTIL_MEAN_C",
    "F_MERCATI_P_MEAN": "F_MERCATI_P_MEAN",
    "F_ASILO_NIDO": "F_ASILO_NIDO",
    "F_ALUNNI_HANDICAP_MEAN": "F_ALUNNI_HANDICAP_MEAN",
    "F_M_PASTI_TOT_P_MEAN": "F_M_PASTI_TOT_P_MEAN",
    "F_M_TRASPORTO_UTENTI_P": "F_M_TRASPORTO_UTENTI_P",
    "F_M_TRASP_DISABILI_P_MEAN": "F_M_TRASP_DISABILI_P_MEAN",
    "F_QUOTA_CLTP_PRIMSEC1": "F_QUOTA_CLTP_PRIMSEC1",
    "F_M_SCUOLE_STAT_COM_N_P": "F_M_SCUOLE_STAT_COM_N_P",
    "F_M_SPAZI_TOT_P": "F_M_SPAZI_TOT_P",
    "F_M_AL_COMUNALI_P_MEAN": "F_M_AL_COMUNALI_P_MEAN",
    "F_M_AL_DISABILI_COMU_P_MEAN": "F_M_AL_DISABILI_COMU_P_MEAN",
    "F_M_AL_PRIVATE_P": "F_M_AL_PRIVATE_P",
    "F_M_PREPOST_ESTIVI_P": "F_M_PREPOST_ESTIVI_P",
    "F_M_QUERELE_P": "F_M_QUERELE_P",
    "F_M_INCIDENTI_P": "F_M_INCIDENTI_P",
    "F_PREZZO_VEIC_FINALE_POL_SCOST": "F_PREZZO_VEIC_FINALE_POL_SCOST",
    "F_OUTPUT_ST_CON_P_LUCE_C": "F_OUTPUT_ST_CON_P_LUCE_C",
    "F_OUTPUT_ALTRI_ESOGENI_P": "F_OUTPUT_ALTRI_ESOGENI_P",
    "F_STALLI_P_MEAN": "F_STALLI_P_MEAN",
    "F_PRESENZE_COMUNE_MEAN": "F_PRESENZE_COMUNE_MEAN",
    "F_ISTAT_GENER_STRADE_KM_MEAN": "F_ISTAT_GENER_STRADE_KM_MEAN",
    "F_ISTAT_SUPERF_TOTALE_KMQ_P": "F_ISTAT_SUPERF_TOTALE_KMQ_P",
    "F_SISMICO_RISCHIO_ALTO": "F_SISMICO_RISCHIO_ALTO",
    "F_DUMMY_ARMATO": "F_DUMMY_ARMATO",
    "F_DUMMY_STRUTTURE": "F_DUMMY_STRUTTURE",
    "F_FASCIA_SON": "F_FASCIA_SON",
    "F_P4_P3_Q": "F_P4_P3_Q",
    "F_DISECONOMIA_SCALA": "F_DISECONOMIA_SCALA",
    "F_VALORE_BENCHMARK_ORE": "F_VALORE_BENCHMARK_ORE",
    "F_VALORE_BENCHMARK_UT": "F_VALORE_BENCHMARK_UT",
    "F_TIPRACCOLTA": "F_TIPRACCOLTA",
    "F_DIFFERENZIATA": "F_DIFFERENZIATA",
    "F_DISTANZA": "F_DISTANZA",
    "F_GESTIONE": "F_GESTIONE",
    "F_INFRASTRUTTURE": "F_INFRASTRUTTURE",
    "F_COSTO_LAV_SCOST_AMM": "F_COSTO_LAV_SCOST_AMM",
    "F_COSTO_LAV_SCOST_IST": "F_COSTO_LAV_SCOST_IST",
    "F_COSTO_LAV_SCOST_POL": "F_COSTO_LAV_SCOST_POL",
    "F_COSTO_LAV_SCOST_TERR": "F_COSTO_LAV_SCOST_TERR",
    "F_COSTO_LAV_SCOST_VIAB": "F_COSTO_LAV_SCOST_VIAB",
    "F_ADDETTI_R_I_2016_N_P": "F_ADDETTI_R_I_2016_N_P",
    "F_ADDETTI_R_I_2018_N_P": "F_ADDETTI_R_I_2018_N_P",
    "D03": "D03",
    "T21": "T21",
}

RDF_NS = "http://purl.org/net/v_ind#"

# Colonne canoniche che clean.sql si aspetta SEMPRE.
# Se una colonna non e' presente nell'RDF di un anno, viene aggiunta vuota.
CANONICAL_COLS = [
    "usr",
    # Spesa standard / storica
    "FST_RIPROPORZIONATO_BI", "FST_RIPROPORZIONATO_BI_PROAB",
    "SPESA_STORICA", "SPESA_STORICA_PROAB",
    # Performance
    "POSIZIONE_OUTPUT_PERC_TOT", "POSIZIONE_SPESA_PERC_TOT",
    "COORD_OUT", "COORD_SPESA",
    "DIFF_OUT_PERC_TOT",
    # Flags
    "FL_SPESA_PIU_OUT_PIU", "FL_SPESA_PIU_OUT_MENO",
    "FL_SPESA_MENO_OUT_MENO", "FL_SPESA_MENO_OUT_PIU",
    "FL_NO_VALUTABILE",
    # Costo lavoro
    "COSTO_LAVORO_PROAB", "DIPENDENTI_X1000AB",
    # Determinanti
    "F_POP_C", "F_DENSITA_MEAN",
    "F_INCID_OLTRE_75_MEAN", "F_INCID_POP_STRA_MEAN",
    "F_INCID_15_64_MEAN", "F_INCID_65_74_MEAN",
    "F_DEPRIVAZIONE_MEAN", "F_DIFF_PENDOLARI_N_P",
    "F_IMMOBILI_TOTALI_P", "F_CONTESTO",
]


def download_and_extract_rdf(url, tmp_dir):
    """Scarica un file ZIP e restituisce il path del file .rdf estratto."""
    zip_path = os.path.join(tmp_dir, "temp.zip")
    try:
        data = download(url, timeout=60)
    except RuntimeError:
        return None
    try:
        with open(zip_path, "wb") as f:
            f.write(data)
        with zipfile.ZipFile(zip_path) as zf:
            rdf_files = [f for f in zf.namelist() if f.endswith(".rdf")]
            if not rdf_files:
                return None
            rdf_name = rdf_files[0]
            zf.extract(rdf_name, tmp_dir)
            return os.path.join(tmp_dir, rdf_name)
    except Exception:
        return None


def parse_rdf_to_rows(rdf_path):
    """Parse XML RDF e restituisce (lista di dict, lista colonne normalizzate)."""
    tree = ET.parse(rdf_path)
    root = tree.getroot()

    rigs = root.findall(f".//{{{RDF_NS}}}rig")
    if not rigs:
        return [], []

    all_cols_set = set()
    rows = []
    for rig in rigs:
        row = {}
        for attr_key, attr_val in rig.attrib.items():
            col_name = attr_key.split("}")[-1] if "}" in attr_key else attr_key
            if col_name in EXCLUDE_COLS:
                continue
            normalized = COL_RENAME.get(col_name, col_name)
            row[normalized] = attr_val.strip() if attr_val else ""
            all_cols_set.add(normalized)
        rows.append(row)

    all_cols = sorted(all_cols_set - {"usr"})
    all_cols = ["usr"] + all_cols
    non_empty_cols = [c for c in all_cols if any(row.get(c, "") for row in rows)]

    return rows, non_empty_cols


def main():
    if len(sys.argv) < 3:
        print("Usage: python preprocess.py <year> <output.csv>", file=sys.stderr)
        sys.exit(1)

    year = int(sys.argv[1])
    output_path = Path(sys.argv[2])

    if year not in YEAR_MAP:
        print(
            f"ERRORE: anno {year} non configurato. Supportati: {list(YEAR_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    prefix, suffix = YEAR_MAP[year]
    url = f"{BASE_URL}/{year}_FC{prefix}TOT_{suffix}_rdf.zip"

    with tempfile.TemporaryDirectory() as tmp_dir:
        rdf_path = download_and_extract_rdf(url, tmp_dir)
        if rdf_path is None:
            print(f"ERRORE: download fallito per {url}", file=sys.stderr)
            sys.exit(1)

        rows, non_empty_cols = parse_rdf_to_rows(rdf_path)
        if not rows:
            print("ERRORE: nessuna riga estratta dal RDF", file=sys.stderr)
            sys.exit(1)


        # Normalizza decimali: virgola -> punto (RDF usa . ma alcuni anni usano ,)
        for row in rows:
            for key, val in row.items():
                if key != "usr" and val and "," in val:
                    row[key] = val.replace(",", ".")

        # Assicura che tutte le colonne canoniche siano presenti (vuote dove mancano)
        final_cols = list(CANONICAL_COLS)
        for col in non_empty_cols:
            if col not in final_cols:
                final_cols.append(col)

        for row in rows:
            for col in CANONICAL_COLS:
                if col not in row:
                    row[col] = ""

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=final_cols,
                delimiter=";",
                extrasaction="ignore",
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        print(
            f"Output: {output_path} ({len(rows)} righe, {len(final_cols)} colonne)",
            flush=True,
        )


if __name__ == "__main__":
    main()
