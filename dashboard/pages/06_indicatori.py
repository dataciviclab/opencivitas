"""Indicatori — Esplorazione metriche per servizio."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import duckdb

from sources import INDI_MART, load_indicatori_comuni, YEARS_DET, load_joined

st.title("📊 Indicatori")
st.markdown("Esplorazione delle metriche di performance per servizio.")

# ── Metriche disponibili ────────────────────────────────────────────────
METRICHE = {
    "🏗️ Rifiuti": {
        "Raccolta differenziata (%)": "raccolta_differenziata_pct",
        "Rifiuti prodotti (kg/ab)": "rifiuti_kg_proab",
    },
    "🎓 Istruzione": {
        "Utenti mensa scolastica (%)": "mensa_scolastica_pct",
        "Mq scuole per ab 3-14": "mq_scuole_per_ab",
        "Utenti trasporti scuola (%)": "trasporti_scuola_pct",
    },
    "👶 Sociale / Nido": {
        "Nido mq/utente": "nido_mq_per_utente",
    },
    "🛣️ Viabilità": {
        "Strade interne (km)": "strade_interne_km",
        "Incidenti per 1000 ab": "incidenti_per1000ab",
    },
    "🏛️ Amministrazione": {
        "Dipendenti per 1000 ab": "dipendenti_per1000ab",
    },
    "👥 Contesto": {
        "Reddito medio IRPEF": "reddito_medio",
        "Pop. straniera (%)": "pop_straniera_pct",
        "Ultra 75enni (%)": "ultra75enni_pct",
        "Bambini 0-2 (%)": "bambini0_2_pct",
        "Pop. 3-14 (%)": "pop_3_14_pct",
    },
}

# Flatten per selectbox
all_metrics = {}
for cat, metrics in METRICHE.items():
    for name, col in metrics.items():
        all_metrics[f"{cat} {name}"] = col

# ── Filtri ──────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    year = st.selectbox("Anno", YEARS_DET, index=YEARS_DET.index(2022) if 2022 in YEARS_DET else 0, key="indi_anno")
with col_f2:
    metrica_label = st.selectbox("Metrica", list(all_metrics.keys()), key="indi_metrica")

col_id = all_metrics[metrica_label]

# ── Carica dati ─────────────────────────────────────────────────────────
df = load_indicatori_comuni(year)
if df.empty:
    st.warning(f"Nessun dato disponibile per il {year}.")
    st.stop()

# Filtra aggregate
df = df[df["comune"].notna() & (df["comune"] != "") & ~df["comune"].str.contains("REGIONE|PROVINCIA", case=False, na=False)]
df_valid = df[df[col_id].notna()].copy()

if df_valid.empty:
    st.warning(f"Nessun dato per {metrica_label} nel {year}.")
    st.stop()

# ── Statistiche ─────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Media nazionale", f"{df_valid[col_id].mean():.1f}")
c2.metric("Mediana", f"{df_valid[col_id].median():.1f}")
c3.metric("Min", f"{df_valid[col_id].min():.1f}")
c4.metric("Max", f"{df_valid[col_id].max():.1f}")

# ── Grafici ─────────────────────────────────────────────────────────────
st.markdown("---")
cg1, cg2 = st.columns(2)

with cg1:
    st.subheader("Distribuzione")
    fig = px.histogram(df_valid, x=col_id, nbins=50, color_discrete_sequence=["#3498db"])
    fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), xaxis_title=metrica_label, yaxis_title="Comuni")
    st.plotly_chart(fig, width="stretch")

with cg2:
    st.subheader("Per regione")
    agg_reg = df_valid.groupby("regione")[col_id].agg(["mean", "median", "count"]).reset_index()
    agg_reg.columns = ["regione", "media", "mediana", "n"]
    agg_reg = agg_reg.sort_values("media", ascending=True)
    fig2 = px.bar(agg_reg, x="media", y="regione", orientation="h", color="media",
                  color_continuous_scale="Blues", text="media")
    fig2.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0), xaxis_title=metrica_label, showlegend=False)
    fig2.update_traces(texttemplate="%.1f", textposition="outside")
    st.plotly_chart(fig2, width="stretch")

# ── Tabella top/bottom ──────────────────────────────────────────────────
st.markdown("---")
n_show = st.slider("Top/Bottom N", 5, 30, 10, key="indi_n")

ct1, ct2 = st.columns(2)
with ct1:
    st.subheader(f"🔝 Top {n_show}")
    top = df_valid.nlargest(n_show, col_id)[["comune", "regione", "fascia_popolazione", col_id]]
    top.columns = ["Comune", "Regione", "Fascia", metrica_label]
    st.dataframe(top.reset_index(drop=True), width="stretch", hide_index=True)

with ct2:
    st.subheader(f"🔻 Bottom {n_show}")
    bottom = df_valid.nsmallest(n_show, col_id)[["comune", "regione", "fascia_popolazione", col_id]]
    bottom.columns = ["Comune", "Regione", "Fascia", metrica_label]
    st.dataframe(bottom.reset_index(drop=True), width="stretch", hide_index=True)

# ── Confronto con media nazionale ────────────────────────────────────────
st.markdown("---")
st.subheader("📍 Confronto con media nazionale")
media_naz = df_valid[col_id].mean()

# Calcola deviazione dalla media
df_valid["delta"] = df_valid[col_id] - media_naz

fig3 = px.scatter(
    df_valid, x="comune", y="delta",
    color="regione",
    hover_data=["comune", "regione", col_id],
    labels={"delta": f"{metrica_label} vs media", "comune": ""},
    color_discrete_sequence=px.colors.qualitative.Set3,
)
fig3.add_hline(y=0, line_dash="dash", line_color="red")
fig3.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=False))
st.plotly_chart(fig3, width="stretch")

st.caption(f"Anno: {year} · Fonte: OpenCivitas (ANCI/Sogei) · CC BY 4.0")
