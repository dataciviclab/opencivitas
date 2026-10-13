-- clean.sql — FPRCM multi-anno: pivot EAV→wide + join geografico
-- Colonne raw sempre per posizione (col0=USERNAME, col1=nome, col2=valore)
-- Header variabile tra anni (VAR_FPRCM_NAME/VAL → Componenti.../Valore):
--   gestito posizionalmente, la riga di header finisce fuori dal filtro IN.

WITH parsed AS (
  SELECT
    normalize_string("column00") AS username,
    normalize_string("column01") AS componente,
    normalize_italian_number("column02") AS valore_num
  FROM raw_input
  WHERE normalize_string("column00") IS NOT NULL
    AND normalize_string("column01") IS NOT NULL
),
fprcm AS (
  SELECT
    username,
    MAX(CASE WHEN componente = 'POPOLAZIONE' THEN valore_num END) AS popolazione,
    MAX(CASE WHEN componente = 'CAPACITA_FISCALI' THEN valore_num END) AS capacita_fiscale,
    MAX(CASE WHEN componente = 'FABBISOGNI_STANDARD' THEN valore_num END) AS fabbisogni_standard,
    MAX(CASE WHEN componente = 'CONTRIBUTO_FONDAMENTALI_PROV' THEN valore_num END) AS contributo_fondamentali_prov,
    MAX(CASE WHEN componente = 'TOTALE_CONTR_FONDI_CORR_2021' THEN valore_num END) AS totale_contributi_fondi_correnti
  FROM parsed
  WHERE componente IN (
    'POPOLAZIONE', 'CAPACITA_FISCALI', 'FABBISOGNI_STANDARD',
    'CONTRIBUTO_FONDAMENTALI_PROV', 'TOTALE_CONTR_FONDI_CORR_2021'
  )
  GROUP BY username
),
enti AS (
  SELECT *
  FROM read_parquet('{support.opencivitas_fprcm_enti.mart}')
)
SELECT
  {year} AS anno,
  fprcm.username,
  enti.denominazione AS ente,
  enti.tipologia_ente,
  enti.provincia,
  enti.regione,
  enti.provincia_istat_cod,
  enti.regione_istat_cod,
  fprcm.popolazione,
  fprcm.capacita_fiscale,
  fprcm.fabbisogni_standard,
  fprcm.contributo_fondamentali_prov,
  fprcm.totale_contributi_fondi_correnti,
  enti.username IS NOT NULL AS join_enti_ok
FROM fprcm
INNER JOIN enti ON fprcm.username = enti.username
WHERE fprcm.username IS NOT NULL
ORDER BY enti.regione, enti.provincia, enti.denominazione
