"""Fonti dati per la dashboard OpenCivitas Intelligence.

Carica i parquet locali via DuckDB: mart_determinanti + FSC.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

# Path base dei dati
BASE = Path(__file__).parent.parent / "out" / "data"

YEARS_DET = [2015, 2016, 2017, 2018, 2019, 2021, 2022]
YEARS_FSC = [2017, 2018, 2020, 2021, 2022, 2023, 2024, 2025]
YEARS_BOTH = sorted(set(YEARS_DET) & set(YEARS_FSC))  # 2017, 2018, 2021, 2022

# Glob patterns
DET_MART = str(BASE / "mart" / "opencivitas_determinanti" / "*" / "mart_determinanti.parquet")
FSC_MART = str(BASE / "mart" / "opencivitas_fsc_rso" / "*" / "mart_compose_comuni.parquet")
INDI_MART = str(BASE / "mart" / "opencivitas_indicatori" / "*" / "mart_comuni.parquet")


@st.cache_data(ttl=3600, show_spinner=False)
def load_determinanti_all() -> pd.DataFrame:
    """Carica il mart_determinanti per tutti gli anni."""
    con = duckdb.connect()
    df = con.execute(f"SELECT * FROM read_parquet('{DET_MART}', union_by_name=true)").fetchdf()
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_determinanti(year: int) -> pd.DataFrame:
    """Carica il mart_determinanti per un anno specifico."""
    con = duckdb.connect()
    path = str(BASE / "mart" / "opencivitas_determinanti" / str(year) / "mart_determinanti.parquet")
    if not Path(path).exists():
        return pd.DataFrame()
    return con.execute(f"SELECT * FROM read_parquet('{path}')").fetchdf()


@st.cache_data(ttl=3600, show_spinner=False)
def load_fsc(year: int) -> pd.DataFrame:
    """Carica il FSC mart per un anno specifico."""
    path = str(BASE / "mart" / "opencivitas_fsc_rso" / str(year) / "mart_compose_comuni.parquet")
    if not Path(path).exists():
        return pd.DataFrame()
    con = duckdb.connect()
    return con.execute(f"SELECT * FROM read_parquet('{path}')").fetchdf()


@st.cache_data(ttl=3600, show_spinner=False)
def load_fsc_all() -> pd.DataFrame:
    """Carica il FSC per tutti gli anni."""
    con = duckdb.connect()
    df = con.execute(f"SELECT * FROM read_parquet('{FSC_MART}', union_by_name=true)").fetchdf()
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_joined(year: int) -> pd.DataFrame:
    """Carica determinanti + FSC joinati su username per un anno."""
    det = load_determinanti(year)
    fsc = load_fsc(year)
    if det.empty or fsc.empty:
        return det if not det.empty else fsc
    # FSC ha province con nomi ISTAT, determinanti pure — join su username
    fsc_cols = ["username", "anno", "popolazione", "capacita_fiscale", "fondo_perequativo",
                "dotazione_finale_fsc", "capacita_fiscale_procapite",
                "fondo_perequativo_procapite", "dotazione_finale_fsc_procapite"]
    fsc_sub = fsc[[c for c in fsc_cols if c in fsc.columns]]
    merged = det.merge(fsc_sub, on=["username", "anno"], how="left", suffixes=("", "_fsc"))
    return merged


@st.cache_data(ttl=3600, show_spinner=False)
def load_joined_all() -> pd.DataFrame:
    """Carica determinanti + FSC joinati per tutti gli anni con overlap."""
    frames = []
    for year in YEARS_BOTH:
        df = load_joined(year)
        if not df.empty:
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def query_det(sql: str) -> pd.DataFrame:
    """Esegue SQL sul mart_determinanti (tutti gli anni)."""
    con = duckdb.connect()
    con.execute(f"CREATE VIEW IF NOT EXISTS _det AS SELECT * FROM read_parquet('{DET_MART}', union_by_name=true)")
    return con.execute(sql).fetchdf()


@st.cache_data(ttl=3600, show_spinner=False)
def load_indicatori_comuni(year: int) -> pd.DataFrame:
    """Carica il mart_comuni (pivot indicatori per comune) per un anno specifico."""
    path = str(BASE / "mart" / "opencivitas_indicatori" / str(year) / "mart_comuni.parquet")
    if not Path(path).exists():
        return pd.DataFrame()
    con = duckdb.connect()
    return con.execute(f"SELECT * FROM read_parquet('{path}')").fetchdf()


@st.cache_data(ttl=3600, show_spinner=False)
def search_comune(q: str, year: int = 2022) -> pd.DataFrame:
    """Cerca un comune per nome (parziale, case-insensitive)."""
    df = load_joined(year)
    if df.empty:
        return df
    mask = df["comune"].str.contains(q, case=False, na=False)
    return df[mask].sort_values("comune")


