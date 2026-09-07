"""Fonti dati per la dashboard OpenCivitas Intelligence.

 usa lab_connectors per auto-detect locale/GCS.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from lab_connectors.duckdb.queries import (
    load_mart_all_years,
    load_mart_table,
    query_clean,
)
from lab_connectors.registry import load_registry

PREFIX = "opencivitas/"

_REPO = Path(__file__).parent.parent
_registry = load_registry(_REPO / "registry" / "registry.json")
_MART_ROOT = _REPO / "out" / "data" / "mart"


def _years_for(slug: str) -> list[int]:
    """Anni dal range period del registry (start..end)."""
    ds = next((d for d in _registry.datasets if d.slug == slug), None)
    if ds is None or not hasattr(ds, "period") or ds.period is None:
        return []
    p = ds.period
    start = getattr(p, "start", None) or (p.get("start") if isinstance(p, dict) else None)
    end = getattr(p, "end", None) or (p.get("end") if isinstance(p, dict) else None)
    if start and end:
        return list(range(int(start), int(end) + 1))
    return []


def _available_years(slug: str) -> list[int]:
    """Anni effettivamente disponibili nei mart parquet (locale o GCS)."""
    slug_dir = _MART_ROOT / slug
    if slug_dir.exists():
        return sorted(int(d.name) for d in slug_dir.iterdir() if d.is_dir() and d.name.isdigit())
    # Fallback: anni dal registry, esclusi quelli noti mancanti nella fonte
    _KNOWN_GAPS = {
        "opencivitas_determinanti": {2020},
        "opencivitas_fsc_rso": {2019},
    }
    gaps = _KNOWN_GAPS.get(slug, set())
    return [y for y in _years_for(slug) if y not in gaps]


YEARS_DET = sorted(set(_years_for("opencivitas_determinanti")) & set(_available_years("opencivitas_determinanti")))
YEARS_FSC = sorted(set(_years_for("opencivitas_fsc_rso")) & set(_available_years("opencivitas_fsc_rso")))
YEARS_BOTH = sorted(set(YEARS_DET) & set(YEARS_FSC))


@st.cache_data(ttl=3600, show_spinner=False)
def load_determinanti(year: int) -> pd.DataFrame:
    return load_mart_table("opencivitas_determinanti", "mart_determinanti", year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_determinanti_all() -> pd.DataFrame:
    return load_mart_all_years("opencivitas_determinanti", "mart_determinanti", YEARS_DET, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_fsc(year: int) -> pd.DataFrame:
    return load_mart_table("opencivitas_fsc_rso", "mart_compose_comuni", year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_fsc_all() -> pd.DataFrame:
    return load_mart_all_years("opencivitas_fsc_rso", "mart_compose_comuni", YEARS_FSC, prefix=PREFIX)


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
