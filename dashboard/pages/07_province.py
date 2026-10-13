"""Province (FPRCM) — Fondo di solidarietà province e città metropolitane."""

import streamlit as st
import pandas as pd

from sources import load_fprcm, YEARS_FPRCM

st.title("🏢 Province — FPRCM")
st.markdown(
    "Fondo di Solidarietà per Province e Città Metropolitane: "
    "fabbisogni, capacità fiscale e contributo fondamentale per ente."
)

# ── Filtri ──────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    year = st.selectbox(
        "Anno", YEARS_FPRCM,
        index=YEARS_FPRCM.index(2026) if 2026 in YEARS_FPRCM else len(YEARS_FPRCM) - 1,
        key="fprcm_anno",
    )
with col_f2:
    ranking = st.selectbox("Ordina per", [
        "Contributo fondamentale €/ab (alta → bassa)",
        "Fabbisogni standard €/ab (alta → bassa)",
        "Capacità fiscale €/ab (alta → bassa)",
        "Gap fabbisogni−capacità €/ab (alta → bassa)",
        "Popolazione (alta → bassa)",
    ], key="fprcm_ranking")

df = load_fprcm(year)
if df.empty:
    st.warning("Nessun dato disponibile per l'anno selezionato.")
    st.stop()

df = df.copy()
df["gap_pc"] = (df["fabbisogni_standard"] - df["capacita_fiscale"]) / df["popolazione"]

# Escludi pseudo-enti non joinati (difesa: ZZ999* già filtrati a monte)
df = df[df["join_enti_ok"] & df["ente"].notna()]

# ── KPI ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Enti", f"{len(df):,}".replace(",", "."))
k2.metric("Tipologie", df["tipologia_ente"].nunique())
contrib_pc = df["contributo_fondamentali_procapite"]
k3.metric("Median contributo €/ab", f"{contrib_pc.median():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k4.metric("Enti con contributo > 0", f"{(contrib_pc > 0).sum()} / {len(df)}")

st.markdown("---")

# ── Tabella ordinata ────────────────────────────────────────────────────
sort_map = {
    "Contributo fondamentale €/ab (alta → bassa)": ("contributo_fondamentali_procapite", False),
    "Fabbisogni standard €/ab (alta → bassa)": ("fabbisogni_standard_procapite", False),
    "Capacità fiscale €/ab (alta → bassa)": ("capacita_fiscale_procapite", False),
    "Gap fabbisogni−capacità €/ab (alta → bassa)": ("gap_pc", False),
    "Popolazione (alta → bassa)": ("popolazione", False),
}
sort_col, ascending = sort_map[ranking]
df_sorted = df.sort_values(sort_col, ascending=ascending, na_position="last")

show_cols = ["ente", "tipologia_ente", "regione", "popolazione",
             "fabbisogni_standard_procapite", "capacita_fiscale_procapite",
             "contributo_fondamentali_procapite", "gap_pc"]
show_cols = [c for c in show_cols if c in df_sorted.columns]
table = df_sorted[show_cols].reset_index(drop=True)
for c in table.select_dtypes("float").columns:
    table[c] = table[c].round(2)

st.dataframe(table, width="stretch", height=min(len(table) * 35 + 40, 700))

st.caption(
    f"Anno: {year} · 86 enti RSO (province, città metropolitane, province montane) · "
    f"Fonte: OpenCivitas (ANCI/Sogei) · CC BY 4.0"
)
