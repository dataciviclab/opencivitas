-- clean.sql — FSC multi-anno: pivot EAV→wide + join geografico
-- Colonne raw sempre per posizione (col0=USERNAME, col1=nome, col2=valore)

WITH parsed AS (
  SELECT
    normalize_string("column00") AS username,
    normalize_string("column01") AS componente,
    normalize_italian_number("column02") AS valore_num
  FROM raw_input
  WHERE normalize_string("column00") IS NOT NULL
    AND normalize_string("column01") IS NOT NULL
),
fsc AS (
  SELECT
    username,
    MAX(CASE WHEN componente = 'POPOLAZIONE' THEN valore_num END) AS popolazione,
    MAX(CASE WHEN componente = 'CAPACITA_FISCALE' THEN valore_num END) AS capacita_fiscale,
    MAX(CASE WHEN componente = 'FONDO_PEREQUATIVO' THEN valore_num END) AS fondo_perequativo,
    MAX(CASE WHEN componente = 'DOTAZIONE_FINALE_FSC' THEN valore_num END) AS dotazione_finale_fsc,
    MAX(CASE WHEN componente = 'IMU_TASI_STANDARD' THEN valore_num END) AS imu_tasi_standard,
    MAX(CASE WHEN componente = 'TOTALE_RISORSE_STORICHE' THEN valore_num END) AS totale_risorse_storiche
  FROM parsed
  WHERE componente IN (
    'POPOLAZIONE', 'CAPACITA_FISCALE', 'FONDO_PEREQUATIVO',
    'DOTAZIONE_FINALE_FSC', 'IMU_TASI_STANDARD', 'TOTALE_RISORSE_STORICHE'
  )
  GROUP BY username
),
enti AS (
  SELECT *
  FROM read_parquet('{support.opencivitas_fsc_enti_rso.mart}')
)
SELECT
  {year} AS anno,
  fsc.username,
  enti.denominazione AS comune,
  enti.provincia,
  enti.regione,
  enti.regione_istat_cod,
  fsc.popolazione,
  fsc.capacita_fiscale,
  fsc.fondo_perequativo,
  fsc.dotazione_finale_fsc,
  fsc.imu_tasi_standard,
  fsc.totale_risorse_storiche,
  enti.username IS NOT NULL AS join_enti_ok
FROM fsc
INNER JOIN enti ON fsc.username = enti.username
WHERE fsc.username IS NOT NULL
ORDER BY enti.regione, enti.provincia, enti.denominazione

