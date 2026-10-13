SELECT
  normalize_string("USERNAME") AS username,
  normalize_string("ENTE") AS denominazione,
  normalize_string("ENTE_TIPOLOGIA") AS tipologia_ente,
  normalize_string("PROVINCIA_DES") AS provincia,
  normalize_string("REGIONE_DES") AS regione,
  cast_int("PROVINCIA_ISTAT_COD") AS provincia_istat_cod,
  cast_int("REGIONE_ISTAT_COD") AS regione_istat_cod
FROM raw_input
WHERE normalize_string("USERNAME") IS NOT NULL
  -- Esclude le 2 righe di intestazione fantasma (ZZ999TIP001/002)
  AND normalize_string("ENTE_TIPOLOGIA") IN ('PROVINCIA', 'CITTAMETROPOLITANA', 'PROVINCIAMONTANA')
