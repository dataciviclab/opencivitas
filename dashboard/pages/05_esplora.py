"""SQL Explorer — Query libera su DuckDB."""

import streamlit as st
import duckdb
import pandas as pd

from sources import DET_MART, FSC_MART

st.title("🧪 SQL Explorer")
st.markdown("Query libera sui dati OpenCivitas via DuckDB.")

# Help
with st.expander("ℹ️ Tabelle disponibili"):
    st.code(f"""
-- Determinanti (spesa standard, performance, quadrant)
-- File: {DET_MART}
SELECT * FROM read_parquet('{DET_MART}', union_by_name=true) LIMIT 5;

-- FSC (capacità fiscale, perequazione, dotazione)
-- File: {FSC_MART}
SELECT * FROM read_parquet('{FSC_MART}', union_by_name=true) LIMIT 5;
""")
    st.markdown("""**Colonne principali (determinanti):**
- `username`, `comune`, `regione`, `provincia`, `anno`
- `popolazione`, `spesa_standard_procapite`, `spesa_storica_procapite`
- `livello_servizi`, `livello_spesa`, `coord_servizi`, `coord_spesa`
- `quadrante`, `fascia_popolazione`
- `capacita_fiscale_procapite`, `fondo_perequativo_procapite`, `dotazione_finale_fsc_procapite`
""")

# Default query
default_sql = """SELECT regione, count(*) as n,
  round(avg(spesa_standard_procapite),0) as std_avg,
  round(avg(livello_servizi),1) as sv_avg,
  round(100.0 * sum(CASE WHEN quadrante = 'spesa_giu_servizi_su' THEN 1 ELSE 0 END) / count(*),1) as eff_pct
FROM read_parquet('" + DET_MART + "', union_by_name=true)
WHERE join_enti_ok = true AND anno = 2022
GROUP BY regione ORDER BY sv_avg DESC"""

sql = st.text_area("SQL", default_sql, height=200, key="esplora_sql")

if st.button("▶️ Esegui", key="esplora_run"):
    try:
        con = duckdb.connect()
        result = con.execute(sql).fetchdf()
        st.success(f"{len(result)} righe")
        st.dataframe(result, width="stretch", height=min(len(result) * 35 + 40, 600))

        # Download CSV
        csv = result.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "query_result.csv", "text/csv")
    except Exception as e:
        st.error(f"Errore: {e}")

st.caption(f"Fonte: OpenCivitas (ANCI/Sogei) · CC BY 4.0")
