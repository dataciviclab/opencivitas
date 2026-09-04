"""Fonti dati per la dashboard OpenCivitas Intelligence.

 usa lab_connectors per auto-detect locale/GCS.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from lab_connectors.duckdb.queries import (
    load_mart_flat,
    load_mart_table,
    query_clean,
    years_from_registry,
)
from lab_connectors.registry import load_registry

PREFIX = "opencivitas/"

_registry = load_registry(Path(__file__).parent.parent / "registry" / "registry.json")
_all_years = years_from_registry(_registry)
YEARS_DET = sorted(y for y in _all_years if y in range(2015, 2023))
YEARS_FSC = sorted(y for y in _all_years if y in range(2017, 2026))
YEARS_BOTH = sorted(set(YEARS_DET) & set(YEARS_FSC))


@st.cache_data(ttl=3600, show_spinner=False)
def load_determinanti(year: int) -> pd.DataFrame:
    return load_mart_table("opencivitas_determinanti", "mart_determinanti", year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_determinanti_all() -> pd.DataFrame:
    return load_mart_flat("opencivitas_determinanti", "mart_determinanti", prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_fsc(year: int) -> pd.DataFrame:
    return load_mart_table("opencivitas_fsc_rso", "mart_compose_comuni", year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_fsc_all() -> pd.DataFrame:
    return load_mart_flat("opencivitas_fsc_rso", "mart_compose_comuni", prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_joined(year: int) -> pd.DataFrame:
    det = load_determinanti(year)
    fsc = load_fsc(year)
    if det.empty or fsc.empty:
        return det if not det.empty else fsc
    fsc_cols = ["username", "anno", "popolazione", "capacita_fiscale", "fondo_perequativo",
                "dotazione_finale_fsc", "capacita_fiscale_procapite",
                "fondo_perequativo_procapite", "dotazione_finale_fsc_procapite"]
    fsc_sub = fsc[[c for c in fsc_cols if c in fsc.columns]]
    return det.merge(fsc_sub, on=["username", "anno"], how="left", suffixes=("", "_fsc"))


@st.cache_data(ttl=3600, show_spinner=False)
def load_joined_all() -> pd.DataFrame:
    frames = []
    for year in YEARS_BOTH:
        df = load_joined(year)
        if not df.empty:
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def load_indicatori_comuni(year: int) -> pd.DataFrame:
    return load_mart_table("opencivitas_indicatori", "mart_comuni", year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def search_comune(q: str, year: int = 2022) -> pd.DataFrame:
    df = load_joined(year)
    if df.empty:
        return df
    mask = df["comune"].str.contains(q, case=False, na=False)
    return df[mask].sort_values("comune")


def get_registry():
    return _registry
