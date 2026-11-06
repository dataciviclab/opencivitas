#!/usr/bin/env python3
"""Scarica il RDF TOT OpenCivitas per un anno e converte in CSV wide.

Fonte: portale Liferay OpenCivitas, RDF TOT diretto (URL con UUID).
Il vecchio dominio docs.opencivitas.it è dismesso.

Il file RDF e' XML con elementi <vi:rig> che hanno attributi = colonne wide.
Le colonne variano tra anni. Questo script le normalizza in nomi canonici.
Output: CSV wide con ; come delimitatore.

Usage: python preprocess.py <year> <output.csv>
"""

import csv
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from lab_connectors.http.download import download

# Portale Liferay OpenCivitas: RDF diretti (URL con UUID). Se un run va in 404,
# recuperare il nuovo URL dall'inventario del catalog-watch (registry/catalog.json).
PORTAL_BASE = "https://www.opencivitas.it/portale/documents/20118/0/"

# anno -> "nome-file/uuid"
PORTAL = {
    2017: "2017_FC40TOT_1/2b0da7cb-b367-4523-a68b-3b4c6a2e94cb",
    2018: "2018_FC50TOT_1/cfb46730-cbc5-8529-cb1e-18eb85f7a267",
    2019: "2019_FC60TOT_2/03d21b26-01b5-b027-9118-5d9cca642fad",
    2021: "2021_FC70TOT_1/231c6dba-1a2e-954e-1723-d9a5a11d304f",
    2022: "2022_FC80TOT_2/7e9b2068-2de1-5ee2-ef53-34d8166e3800",
    2023: "2023_FC90_TOT_1_IT.rdf/a1a8327c-6493-e0b7-d5ac-9284751e81c7",
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


def download_rdf(url, tmp_dir):
    """Scarica il file RDF diretto e restituisce il path locale."""
    rdf_path = os.path.join(tmp_dir, "tot.rdf")
    try:
        data = download(url, timeout=60)
    except RuntimeError:
        return None
    try:
        with open(rdf_path, "wb") as f:
            f.write(data)
        return rdf_path
    except Exception:
        return None


def _iter_rig_attrs(rdf_path):
    """Estrae gli attributi di ogni <vi:rig> come {nome_locale: valore}.

    Usa ElementTree; se il file è XML malformato (es. il RDF 2022 del portale
    ha header rotto e path locali Sogei) ricade su una scansione tollerante:
    gli elementi <vi:rig ... /> sono self-contained e integri.
    """
    try:
        tree = ET.parse(rdf_path)
        root = tree.getroot()
        rigs = root.findall(f".//{{{RDF_NS}}}rig")
        if rigs:
            out = []
            for rig in rigs:
                out.append(
                    {
                        (k.split("}")[-1] if "}" in k else k): v
                        for k, v in rig.attrib.items()
                    }
                )
            return out
    except ET.ParseError:
        pass

    with open(rdf_path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    out = []
    for attrs in re.findall(r"<vi:rig\b([^>]*?)/>", text):
        out.append({m.group(1).split(":")[-1]: m.group(2) for m in re.finditer(r'([\w:]+)="([^"]*)"', attrs)})
    return out


def parse_rdf_to_rows(rdf_path):
    """Parse XML RDF e restituisce (lista di dict, lista colonne normalizzate)."""
    rigs = _iter_rig_attrs(rdf_path)
    if not rigs:
        return [], []

    all_cols_set = set()
    rows = []
    for attrs in rigs:
        row = {}
        for col_name, attr_val in attrs.items():
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

    if year not in PORTAL:
        print(
            f"ERRORE: anno {year} non configurato. Supportati: {sorted(PORTAL.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    url = f"{PORTAL_BASE}{PORTAL[year]}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        rdf_path = download_rdf(url, tmp_dir)
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
