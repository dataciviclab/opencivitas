-- clean.sql — Determinanti OpenCivitas: spesa standard + performance scores + determinanti
-- Input: raw_input.csv (CSV wide da preprocess.py, generato dal RDF XML)
-- Output: wide con username, geografia, spesa standard/storica, performance, determinanti
--
-- Le colonne variano tra anni (84-98). DuckDB legge solo quelle presenti.
-- Normalizziamo i nomi colonne e uniamo con anagrafica enti.

WITH parsed AS (
  SELECT
    normalize_string("usr") AS username,
    -- Spesa standard (dotazione) — RDF usa punto come decimale
    TRY_CAST("FST_RIPROPORZIONATO_BI" AS DOUBLE) AS spesa_standard,
    TRY_CAST("FST_RIPROPORZIONATO_BI_PROAB" AS DOUBLE) AS spesa_standard_procapite,
    -- Spesa storica
    TRY_CAST("SPESA_STORICA" AS DOUBLE) AS spesa_storica,
    TRY_CAST("SPESA_STORICA_PROAB" AS DOUBLE) AS spesa_storica_procapite,
    -- Performance scores (0-10)
    TRY_CAST("POSIZIONE_OUTPUT_PERC_TOT" AS DOUBLE) AS livello_servizi,
    TRY_CAST("POSIZIONE_SPESA_PERC_TOT" AS DOUBLE) AS livello_spesa,
    -- Coordinate performance (-5 a +5)
    TRY_CAST("COORD_OUT" AS DOUBLE) AS coord_servizi,
    TRY_CAST("COORD_SPESA" AS DOUBLE) AS coord_spesa,
    -- Quadrant flags
    TRY_CAST("FL_SPESA_PIU_OUT_PIU" AS DOUBLE) AS flag_spesa_su_servizi_su,
    TRY_CAST("FL_SPESA_PIU_OUT_MENO" AS DOUBLE) AS flag_spesa_su_servizi_giu,
    TRY_CAST("FL_SPESA_MENO_OUT_MENO" AS DOUBLE) AS flag_spesa_giu_servizi_giu,
    TRY_CAST("FL_SPESA_MENO_OUT_PIU" AS DOUBLE) AS flag_spesa_giu_servizi_su,
    TRY_CAST("FL_NO_VALUTABILE" AS DOUBLE) AS flag_non_valutabile,
    -- Costo del lavoro
    TRY_CAST("COSTO_LAVORO_PROAB" AS DOUBLE) AS costo_lavoro_procapite,
    TRY_CAST("DIPENDENTI_X1000AB" AS DOUBLE) AS dipendenti_x1000ab,
    -- Confronto
    TRY_CAST("DIFF_OUT_PERC_TOT" AS DOUBLE) AS diff_servizi_pct,
    -- Determinanti demografiche/socio-economiche (colonne F_*)
    -- NOTA: F_POP_C non esiste nei dati 2015-2016, TRY_CAST restituirà NULL
    TRY_CAST("F_POP_C" AS DOUBLE) AS det_popolazione,
    TRY_CAST("F_DENSITA_MEAN" AS DOUBLE) AS det_densita,
    TRY_CAST("F_INCID_OLTRE_75_MEAN" AS DOUBLE) AS det_ultra_75,
    TRY_CAST("F_INCID_POP_STRA_MEAN" AS DOUBLE) AS det_pop_straniera,
    TRY_CAST("F_INCID_15_64_MEAN" AS DOUBLE) AS det_pop_15_64,
    TRY_CAST("F_INCID_65_74_MEAN" AS DOUBLE) AS det_pop_65_74,
    TRY_CAST("F_DEPRIVAZIONE_MEAN" AS DOUBLE) AS det_deprivazione,
    TRY_CAST("F_DIFF_PENDOLARI_N_P" AS DOUBLE) AS det_pendolari,
    TRY_CAST("F_IMMOBILI_TOTALI_P" AS DOUBLE) AS det_immobili,
    TRY_CAST("F_CONTESTO" AS DOUBLE) AS det_fattore_contesto
  FROM raw_input
  WHERE normalize_string("usr") IS NOT NULL
),
enti AS (
  SELECT *
  FROM read_parquet('{support.opencivitas_fsc_enti_rso.mart}')
)
SELECT
  {year} AS anno,
  p.username,
  e.denominazione AS comune,
  e.provincia,
  e.regione,
  e.regione_istat_cod,
  -- Spesa standard vs storica
  p.spesa_standard,
  p.spesa_standard_procapite,
  p.spesa_storica,
  p.spesa_storica_procapite,
  -- Rapporto spesa standard / storica
  CASE
    WHEN p.spesa_storica > 0 THEN p.spesa_standard / p.spesa_storica
    ELSE NULL
  END AS rapporto_standard_storico,
  -- Performance
  p.livello_servizi,
  p.livello_spesa,
  p.coord_servizi,
  p.coord_spesa,
  -- Quadrant
  p.flag_spesa_su_servizi_su,
  p.flag_spesa_su_servizi_giu,
  p.flag_spesa_giu_servizi_giu,
  p.flag_spesa_giu_servizi_su,
  p.flag_non_valutabile,
  -- Costo lavoro
  p.costo_lavoro_procapite,
  p.dipendenti_x1000ab,
  p.diff_servizi_pct,
  -- Determinanti
  p.det_popolazione,
  p.det_densita,
  p.det_ultra_75,
  p.det_pop_straniera,
  p.det_pop_15_64,
  p.det_pop_65_74,
  p.det_deprivazione,
  p.det_pendolari,
  p.det_immobili,
  p.det_fattore_contesto,
  -- Join quality
  e.username IS NOT NULL AS join_enti_ok
FROM parsed p
LEFT JOIN enti e ON p.username = e.username
WHERE p.username IS NOT NULL
ORDER BY e.regione, e.provincia, e.denominazione
