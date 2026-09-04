"""Profilo Comune — Scheda completa: quadrant, spesa, performance, FSC."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from sources import load_joined, load_joined_all, search_comune, YEARS_BOTH

st.title("🏛️ Profilo Comune")
st.markdown("Scheda completa: quadrant di performance, spesa vs standard, FSC.")

# ── Ricerca ─────────────────────────────────────────────────────────────
col_s, col_y = st.columns([3, 1])
with col_s:
    q = st.text_input("Cerca comune", placeholder="es. Prato, Milano, Roma...", key="profilo_q")
with col_y:
    year = st.selectbox("Anno", YEARS_BOTH, index=YEARS_BOTH.index(2022) if 2022 in YEARS_BOTH else 0, key="profilo_anno")

if not q:
    st.info("Inserisci il nome di un comune per vedere il profilo completo.")
    st.stop()

matches = search_comune(q, year)
if matches.empty:
    st.warning(f"Nessun comune trovato per '{q}'.")
    st.stop()

# Se c'è più di un match, lascia scegliere
if len(matches) > 1:
    options = [f"{r['comune']} ({r.get('regione','')})" for _, r in matches.iterrows()]
    choice = st.selectbox(f"{len(matches)} risultati", options, key="profilo_choice")
    idx = options.index(choice)
    row = matches.iloc[idx]
else:
    row = matches.iloc[0]

comune = row["comune"]
regione = row.get("regione", "-")

# ── Header ──────────────────────────────────────────────────────────────
st.markdown(f"### {comune} ({regione}) — {year}")

# Quadrant badge
q_map = {
    "spesa_giu_servizi_su": ("✅ Efficiente", "#2ecc71"),
    "spesa_su_servizi_su": ("💰 Virtuoso", "#3498db"),
    "spesa_giu_servizi_giu": ("⚠️ Sotto-finanziato", "#f39c12"),
    "spesa_su_servizi_giu": ("🔴 Inefficiente", "#e74c3c"),
    "non_valutabile": ("❓ Non valutabile", "#95a5a6"),
}
quad = row.get("quadrante", "")
if quad in q_map:
    label, color = q_map[quad]
    st.markdown(f"<span style='background:{color};color:white;padding:4px 12px;border-radius:4px;font-size:18px'>{label}</span>", unsafe_allow_html=True)

# ── Metriche chiave ────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Popolazione", f"{row.get('popolazione', 0):,.0f}")
c2.metric("Spesa standard €/ab", f"{row.get('spesa_standard_procapite', 0):,.0f}")
c3.metric("Spesa storica €/ab", f"{row.get('spesa_storica_procapite', 0):,.0f}")
c4.metric("Servizi (0-10)", f"{row.get('livello_servizi', 0):.1f}")
c5.metric("Spesa (0-10)", f"{row.get('livello_spesa', 0):.1f}")

# ── Grafici ─────────────────────────────────────────────────────────────
st.markdown("---")
cg1, cg2 = st.columns(2)

with cg1:
    st.subheader("Spesa vs Standard")
    std = row.get("spesa_standard_procapite", 0) or 0
    stor = row.get("spesa_storica_procapite", 0) or 0
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Standard"], y=[std], name="Standard", marker_color="#3498db"))
    fig.add_trace(go.Bar(x=["Storica"], y=[stor], name="Storica", marker_color="#2ecc71" if stor <= std else "#e74c3c"))
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="€/abitante", showlegend=False)
    st.plotly_chart(fig, width="stretch")

with cg2:
    st.subheader("Coordinate Performance")
    co = row.get("coord_servizi", 0) or 0
    cs = row.get("coord_spesa", 0) or 0
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=[cs], y=[co], mode="markers+text", text=[comune],
                              textposition="top center", marker=dict(size=20, color=color)))
    fig2.add_vline(x=0, line_dash="dash", line_color="gray")
    fig2.add_hline(y=0, line_dash="dash", line_color="gray")
    fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                       xaxis_title="Spesa (← bassa | alta →)", yaxis_title="Servizi (↓ bassi | alti ↑)",
                       xaxis_range=[-6, 6], yaxis_range=[-6, 6])
    st.plotly_chart(fig2, width="stretch")

# ── FSC (se disponibile) ────────────────────────────────────────────────
if pd.notna(row.get("capacita_fiscale_procapite")):
    st.markdown("---")
    st.subheader("💰 FSC — Finanza comunale")
    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Capacità fiscale €/ab", f"{row.get('capacita_fiscale_procapite', 0):,.0f}")
    fc2.metric("Fondo perequativo €/ab", f"{row.get('fondo_perequativo_procapite', 0):,.0f}")
    fc3.metric("Dotazione FSC €/ab", f"{row.get('dotazione_finale_fsc_procapite', 0):,.0f}")

# ── Trend temporale ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Trend")
df_all = load_joined_all()
if not df_all.empty:
    trend = df_all[df_all["comune"] == comune].sort_values("anno")
    if not trend.empty:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=trend["anno"], y=trend["spesa_standard_procapite"],
                                  name="Standard", line=dict(color="#3498db")))
        fig3.add_trace(go.Scatter(x=trend["anno"], y=trend["spesa_storica_procapite"],
                                  name="Storica", line=dict(color="#2ecc71")))
        fig3.add_trace(go.Scatter(x=trend["anno"], y=trend["livello_servizi"],
                                  name="Servizi", line=dict(color="#e74c3c"), yaxis="y2"))
        fig3.update_layout(
            height=350, margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(title="€/abitante"),
            yaxis2=dict(title="Servizi (0-10)", overlaying="y", side="right", range=[0, 10]),
            legend=dict(x=0, y=1.1, orientation="h"),
        )
        st.plotly_chart(fig3, width="stretch")
    else:
        st.caption("Nessun dato trend disponibile per questo comune.")

# ── Tabella dettaglio ───────────────────────────────────────────────────
st.markdown("---")
st.subheader("Dati completi")
show_cols = ["anno", "popolazione", "spesa_standard_procapite", "spesa_storica_procapite",
             "rapporto_standard_storico", "livello_servizi", "livello_spesa",
             "quadrante", "fascia_popolazione",
             "capacita_fiscale_procapite", "fondo_perequativo_procapite", "dotazione_finale_fsc_procapite"]
show_cols = [c for c in show_cols if c in trend.columns] if not trend.empty else []
if show_cols and not trend.empty:
    st.dataframe(trend[show_cols].reset_index(drop=True), width="stretch")

st.caption(f"Fonte: OpenCivitas (ANCI/Sogei) · CC BY 4.0")
