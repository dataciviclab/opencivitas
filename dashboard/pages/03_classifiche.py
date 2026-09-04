"""Classifiche — Ranking comuni per efficienza, spesa, servizi."""

import streamlit as st
import pandas as pd

from sources import load_joined, YEARS_BOTH

st.title("🏆 Classifiche")
st.markdown("Ranking dei comuni per diverse metriche.")

# ── Filtri ──────────────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    year = st.selectbox("Anno", YEARS_BOTH, index=YEARS_BOTH.index(2022) if 2022 in YEARS_BOTH else 0, key="class_anno")
with col_f2:
    ranking = st.selectbox("Ranking per", [
        "Efficienza (servizi / spesa)",
        "Spesa storica €/ab (alta → bassa)",
        "Spesa standard €/ab (alta → bassa)",
        "Livello servizi (0-10)",
        "Capacità fiscale €/ab (FSC)",
    ], key="class_ranking")
with col_f3:
    fascia = st.selectbox("Fascia popolazione", ["Tutte"] + [
        "01_micro <1k", "02_piccolo 1-5k", "03_medio 5-15k", "04_grande 15-50k", "05_metro 50k+"
    ], key="class_fascia")

n_top = st.slider("Mostra top/bottom N", 5, 50, 15, key="class_n")

df = load_joined(year)
if df.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

# Filtra per fascia
if fascia != "Tutte":
    df = df[df["fascia_popolazione"] == fascia]

# Escludi aggregati regionali
df = df[df["comune"].notna() & (df["comune"] != "") & ~df["comune"].str.contains("REGIONE|PROVINCIA", case=False, na=False)]
# Filtra aggregate (flag non binari)
flag_cols = ["flag_spesa_su_servizi_su", "flag_spesa_su_servizi_giu",
             "flag_spesa_giu_servizi_giu", "flag_spesa_giu_servizi_su"]
for fc in flag_cols:
    if fc in df.columns:
        df = df[df[fc].isin([0, 1, 0.0, 1.0, None])]

# Calcola metrica ranking
if "Efficienza" in ranking:
    df["_rank"] = df["livello_servizi"] / df["spesa_storica_procapite"].replace(0, float("nan"))
    ascending = False
elif "Spesa storica" in ranking:
    df["_rank"] = df["spesa_storica_procapite"]
    ascending = False
elif "Spesa standard" in ranking:
    df["_rank"] = df["spesa_standard_procapite"]
    ascending = False
elif "Livello servizi" in ranking:
    df["_rank"] = df["livello_servizi"]
    ascending = False
elif "Capacità fiscale" in ranking:
    df["_rank"] = df["capacita_fiscale_procapite"]
    ascending = False
else:
    df["_rank"] = 0
    ascending = False

df_sorted = df.dropna(subset=["_rank"]).sort_values("_rank", ascending=ascending, na_position="last")

# ── Top N ───────────────────────────────────────────────────────────────
st.subheader(f"🔝 Top {n_top}")
top = df_sorted.head(n_top)
show_cols = ["comune", "regione", "fascia_popolazione", "popolazione",
             "spesa_standard_procapite", "spesa_storica_procapite",
             "livello_servizi", "livello_spesa", "quadrante"]
show_cols = [c for c in show_cols if c in top.columns]
st.dataframe(top[show_cols].reset_index(drop=True), width="stretch", height=min(n_top * 35 + 40, 600))

# ── Bottom N ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader(f"🔻 Bottom {n_top}")
bottom = df_sorted.tail(n_top).sort_values("_rank", ascending=ascending)
st.dataframe(bottom[show_cols].reset_index(drop=True), width="stretch", height=min(n_top * 35 + 40, 600))

st.caption(f"Anno: {year} · Fonte: OpenCivitas (ANCI/Sogei) · CC BY 4.0")
