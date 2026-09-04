"""Mappa Italia — Quadrant performance + spesa standard per regione."""

import streamlit as st
import plotly.express as px

from sources import load_joined, YEARS_BOTH

st.title("🗺️ Mappa Italia")
st.markdown("Distribuzione geografica del quadrant di performance e spesa standard.")

# ── Filtri ──────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    year = st.selectbox(
        "Anno",
        YEARS_BOTH,
        index=YEARS_BOTH.index(2022) if 2022 in YEARS_BOTH else 0,
        key="mappa_anno",
    )
with col_f2:
    metrica = st.radio(
        "Metrica",
        ["Quadrant", "Spesa standard €/ab", "Spesa storica €/ab", "Livello servizi"],
        horizontal=True,
        key="mappa_metrica",
    )

df = load_joined(year)
if df.empty:
    st.warning(f"Nessun dato disponibile per il {year}.")
    st.stop()

# ── Aggregazione per regione ────────────────────────────────────────────
df_reg = df[
    (df["regione"].notna()) &
    (df["regione"] != "") &
    (df["regione"] != "ITALIA") &
    (df["comune"].notna()) &
    (df["comune"] != "") &
    ~df["comune"].str.contains("REGIONE|PROVINCIA", case=False, na=False)
].copy()

# Filtra righe con flag non binari (aggregate rovinate)
flag_cols = ["flag_spesa_su_servizi_su", "flag_spesa_su_servizi_giu",
             "flag_spesa_giu_servizi_giu", "flag_spesa_giu_servizi_su"]
for fc in flag_cols:
    if fc in df_reg.columns:
        df_reg = df_reg[df_reg[fc].isin([0, 1, 0.0, 1.0, None])]

if metrica == "Quadrant":
    # Conta quadrant per regione
    agg = df_reg.groupby("regione").agg(
        n_comuni=("username", "count"),
        pct_efficiente=("flag_spesa_giu_servizi_su", "mean"),
        pct_sottofin=("flag_spesa_giu_servizi_giu", "mean"),
        pct_spreco=("flag_spesa_su_servizi_giu", "mean"),
    ).reset_index()
    agg["pct_efficiente"] = (agg["pct_efficiente"] * 100).round(1)
    agg["pct_sottofin"] = (agg["pct_sottofin"] * 100).round(1)
    agg["pct_spreco"] = (agg["pct_spreco"] * 100).round(1)
    color_col = "pct_efficiente"
    color_label = "% Efficienti (D)"
    hover_data = {"pct_efficiente": ":.1f%", "pct_sottofin": ":.1f%", "pct_spreco": ":.1f%", "n_comuni": True}
else:
    col_map = {
        "Spesa standard €/ab": "spesa_standard_procapite",
        "Spesa storica €/ab": "spesa_storica_procapite",
        "Livello servizi": "livello_servizi",
    }
    col_id = col_map[metrica]
    agg = df_reg.groupby("regione").agg(
        media=(col_id, "mean"),
        n_comuni=("username", "count"),
    ).reset_index()
    agg["media"] = agg["media"].round(1)
    color_col = "media"
    color_label = metrica
    hover_data = {"media": ":,.1f", "n_comuni": True}

agg["label_geo"] = agg["regione"].str.title()

# ── Mappa ───────────────────────────────────────────────────────────────
st.subheader(f"{metrica} — {year}")

GEOJSON_URL = "https://raw.githubusercontent.com/guglielmo/geojson-italy/master/geojson/limits_IT_regions.geojson"

fig = px.choropleth(
    agg,
    geojson=GEOJSON_URL,
    locations="label_geo",
    featureidkey="properties.reg_name",
    color=color_col,
    color_continuous_scale="RdYlGn" if metrica == "Quadrant" else "Blues",
    hover_name="regione",
    hover_data=hover_data,
    labels={color_col: color_label, "n_comuni": "Comuni"},
)
fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    height=500,
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, width="stretch")

# ── Statistiche regionali ──────────────────────────────────────────────
st.markdown("---")

if metrica == "Quadrant":
    st.subheader("Distribuzione quadrant per regione")
    show = agg[["regione", "n_comuni", "pct_efficiente", "pct_sottofin", "pct_spreco"]].sort_values(
        "pct_efficiente", ascending=False
    )
    show.columns = ["Regione", "Comuni", "% Efficienti (D)", "% Sottofinanziati (C)", "% Spreco (B)"]
    st.dataframe(show.reset_index(drop=True), width="stretch", height=500,
                 column_config={c: st.column_config.NumberColumn(c, format="%.1f%%") for c in show.columns[2:]})
else:
    st.subheader(f"Ranking regioni — {metrica}")
    show = agg[["regione", "media", "n_comuni"]].sort_values("media", ascending=False)
    show.columns = ["Regione", metrica, "Comuni"]
    st.dataframe(show.reset_index(drop=True), width="stretch", height=500)

st.caption(f"Anno: {year} · Fonte: OpenCivitas (ANCI/Sogei) · CC BY 4.0")

