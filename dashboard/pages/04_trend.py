"""Trend — Evoluzione quadrant e metriche nel tempo."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from sources import load_determinanti_all, YEARS_DET

st.title("📈 Trend")
st.markdown("Evoluzione delle performance dei comuni italiani nel tempo.")

df = load_determinanti_all()
if df.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

df = df[df["join_enti_ok"] == True].copy()

# ── Quadrant nel tempo ──────────────────────────────────────────────────
st.subheader("Evoluzione Quadrant")
agg = df.groupby("anno").agg(
    n=("username", "count"),
    pct_A=("flag_spesa_su_servizi_su", "mean"),
    pct_B=("flag_spesa_su_servizi_giu", "mean"),
    pct_C=("flag_spesa_giu_servizi_giu", "mean"),
    pct_D=("flag_spesa_giu_servizi_su", "mean"),
).reset_index()
for c in ["pct_A", "pct_B", "pct_C", "pct_D"]:
    agg[c] = (agg[c] * 100).round(1)

fig = go.Figure()
fig.add_trace(go.Scatter(x=agg["anno"], y=agg["pct_D"], name="D: spesa- servizi+", fill="tozeroy", line=dict(color="#2ecc71")))
fig.add_trace(go.Scatter(x=agg["anno"], y=agg["pct_A"], name="A: spesa+ servizi+", fill="tozeroy", line=dict(color="#3498db")))
fig.add_trace(go.Scatter(x=agg["anno"], y=agg["pct_C"], name="C: spesa- servizi-", line=dict(color="#f39c12")))
fig.add_trace(go.Scatter(x=agg["anno"], y=agg["pct_B"], name="B: spesa+ servizi-", line=dict(color="#e74c3c")))
fig.update_layout(height=400, yaxis_title="% comuni", xaxis_title="Anno", legend=dict(x=0, y=1.1, orientation="h"))
st.plotly_chart(fig, use_container_width=True)

# ── Tabella riassuntiva ────────────────────────────────────────────────
st.dataframe(agg.rename(columns={
    "anno": "Anno", "n": "N comuni",
    "pct_A": "A%", "pct_B": "B%", "pct_C": "C%", "pct_D": "D%"
}), hide_index=True, use_container_width=True)

# ── Spesa media nel tempo ───────────────────────────────────────────────
st.markdown("---")
st.subheader("Spesa standard vs storica (media nazionale)")
agg2 = df.groupby("anno").agg(
    std=("spesa_standard_procapite", "mean"),
    stor=("spesa_storica_procapite", "mean"),
    sv=("livello_servizi", "mean"),
).reset_index()

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=agg2["anno"], y=agg2["std"], name="Standard €/ab", line=dict(color="#3498db")))
fig2.add_trace(go.Scatter(x=agg2["anno"], y=agg2["stor"], name="Storica €/ab", line=dict(color="#2ecc71")))
fig2.update_layout(height=350, yaxis_title="€/abitante", legend=dict(x=0, y=1.1, orientation="h"))
st.plotly_chart(fig2, use_container_width=True)

# ── Servizi nel tempo ───────────────────────────────────────────────────
st.subheader("Livello servizi medio")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=agg2["anno"], y=agg2["sv"], name="Servizi", line=dict(color="#e74c3c"), fill="tozeroy"))
fig3.update_layout(height=250, yaxis_title="0-10", yaxis_range=[0, 10])
st.plotly_chart(fig3, use_container_width=True)

st.caption(f"Fonte: OpenCivitas (ANCI/Sogei) · CC BY 4.0")
