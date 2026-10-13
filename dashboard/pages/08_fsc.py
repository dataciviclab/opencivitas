"""FSC — Fondi di solidarietà comunale: classifiche e trend (2017-2026)."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from sources import load_fsc, load_fsc_all, YEARS_FSC

st.title("💰 FSC — Fondi comunali")
st.markdown(
    "Fondo di Solidarietà Comunale (RSO): fondi perequativi, dotazione finale "
    "e capacità fiscale per comune. Serie estesa al 2026."
)

# ── Filtri ──────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    year = st.selectbox(
        "Anno", YEARS_FSC,
        index=YEARS_FSC.index(2026) if 2026 in YEARS_FSC else len(YEARS_FSC) - 1,
        key="fsc_anno",
    )
with col_f2:
    ranking = st.selectbox("Ordina per", [
        "Fondo perequativo €/ab (alta → bassa)",
        "Dotazione finale €/ab (alta → bassa)",
        "Capacità fiscale €/ab (alta → bassa)",
        "Popolazione (alta → bassa)",
    ], key="fsc_ranking")

df = load_fsc(year)
if df.empty:
    st.warning("Nessun dato disponibile per l'anno selezionato.")
    st.stop()

df = df[df["join_enti_ok"] & df["comune"].notna()].copy()

# ── KPI ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Comuni", f"{len(df):,}".replace(",", "."))
k2.metric("Median fondo perequativo €/ab", f"{df['fondo_perequativo_procapite'].median():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k3.metric("Median dotazione finale €/ab", f"{df['dotazione_finale_fsc_procapite'].median():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k4.metric("Median capacità fiscale €/ab", f"{df['capacita_fiscale_procapite'].median():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# ── Classifiche ─────────────────────────────────────────────────────────
sort_map = {
    "Fondo perequativo €/ab (alta → bassa)": ("fondo_perequativo_procapite", False),
    "Dotazione finale €/ab (alta → bassa)": ("dotazione_finale_fsc_procapite", False),
    "Capacità fiscale €/ab (alta → bassa)": ("capacita_fiscale_procapite", False),
    "Popolazione (alta → bassa)": ("popolazione", False),
}
sort_col, ascending = sort_map[ranking]
df_sorted = df.sort_values(sort_col, ascending=ascending, na_position="last")

show_cols = ["comune", "regione", "popolazione",
             "fondo_perequativo_procapite", "dotazione_finale_fsc_procapite",
             "capacita_fiscale_procapite"]
show_cols = [c for c in show_cols if c in df_sorted.columns]
table = df_sorted[show_cols].reset_index(drop=True)
for c in table.select_dtypes("float").columns:
    table[c] = table[c].round(2)

st.dataframe(table, width="stretch", height=min(len(table) * 35 + 40, 700))

st.markdown("---")

# ── Trend nazionale ─────────────────────────────────────────────────────
st.subheader("Evoluzione nazionale (media €/ab)")

fsc_all = load_fsc_all()
if not fsc_all.empty:
    fsc_all = fsc_all[fsc_all["join_enti_ok"] == True]
    agg = fsc_all.groupby("anno").agg(
        n=("username", "count"),
        fondi=("fondo_perequativo_procapite", "mean"),
        dotazione=("dotazione_finale_fsc_procapite", "mean"),
        capacita=("capacita_fiscale_procapite", "mean"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=agg["anno"], y=agg["fondi"], name="Fondo perequativo", line=dict(color="#3498db")))
    fig.add_trace(go.Scatter(x=agg["anno"], y=agg["dotazione"], name="Dotazione finale", line=dict(color="#2ecc71")))
    fig.add_trace(go.Scatter(x=agg["anno"], y=agg["capacita"], name="Capacità fiscale", line=dict(color="#f39c12")))
    fig.update_layout(height=400, yaxis_title="€/abitante", legend=dict(x=0, y=1.1, orientation="h"))
    st.plotly_chart(fig, width="stretch")

    st.dataframe(agg.rename(columns={
        "anno": "Anno", "n": "N comuni",
        "fondi": "Fondo perequativo €/ab",
        "dotazione": "Dotazione finale €/ab",
        "capacita": "Capacità fiscale €/ab",
    }).round(2), hide_index=True, width="stretch")

st.caption(
    f"Anni: {YEARS_FSC[0]}–{YEARS_FSC[-1]} (salto 2019, mai pubblicato) · "
    f"Fonte: OpenCivitas (ANCI/Sogei) · CC BY 4.0"
)
