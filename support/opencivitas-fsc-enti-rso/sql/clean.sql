SELECT
  normalize_string("USERNAME") AS username,
  normalize_string("DENOMINAZIONE") AS denominazione,
  normalize_string("PROVINCIA") AS provincia,
  normalize_string("REGIONE_DES") AS regione,
  cast_int("REGIONE_ISTAT_COD") AS regione_istat_cod
FROM raw_input
WHERE normalize_string("USERNAME") IS NOT NULL

