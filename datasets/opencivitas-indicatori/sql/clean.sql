-- clean.sql — normalizza EAV indicatori + join anagrafica enti + descrizione indicatori
-- Input: raw_input.csv (da preprocess.py)
-- Output: clean con denominazione, provincia, regione, descrizione_indicatore
-- NOTA: il glossario ha nomi diversi per anno (es. RACC_DIFFER_PERC_2017 vs RACC_DIFFER_PERC)
--       quindi carichiamo TUTTI gli anni e usiamo LIKE per il join

WITH parsed AS (
  SELECT
    normalize_string("username") AS username,
    cast_int("anno") AS anno,
    normalize_string("ambito") AS ambito,
    normalize_string("indicatore") AS indicatore,
    -- Formato valore: 2015-2016 usa punto (27.15), 2017-2022 usa virgola (25,83)
    -- Gestiamo entrambi: se c'è virgola, usa normalize_italian_number; altrimenti cast_double
    CASE
      WHEN CONTAINS("valore", ',') THEN normalize_italian_number("valore")
      ELSE cast_double("valore")
    END AS valore_num
  FROM raw_input
  WHERE normalize_string("username") IS NOT NULL
    AND normalize_string("indicatore") IS NOT NULL
),
enti AS (
  SELECT *
  FROM read_parquet('{support.opencivitas_fsc_enti_rso.mart}')
),
metadati AS (
  SELECT codice_indicatore, descrizione, tipo, categoria, funzione, anno, ambito
  FROM read_parquet(
      '{root}/data/mart/opencivitas_glossario/*/*_metadati.parquet',
      union_by_name=true
  )
)
SELECT
  p.username,
  p.anno,
  p.ambito,
  p.indicatore,
  p.valore_num,
  m.descrizione AS descrizione_indicatore,
  m.tipo AS tipo_indicatore,
  m.categoria AS categoria_indicatore,
  m.funzione AS funzione_indicatore,
  e.denominazione,
  e.provincia,
  e.regione,
  e.regione_istat_cod,
  e.denominazione IS NOT NULL AS join_enti_ok,
  m.descrizione IS NOT NULL AS join_metadati_ok
FROM parsed p
LEFT JOIN enti e ON p.username = e.username
LEFT JOIN metadati m ON p.indicatore = m.codice_indicatore
                   AND p.ambito = m.ambito
                   AND p.anno = m.anno
WHERE p.anno IS NOT NULL
  AND p.valore_num IS NOT NULL
ORDER BY p.anno, p.ambito, e.regione, e.provincia, e.denominazione, p.indicatore

