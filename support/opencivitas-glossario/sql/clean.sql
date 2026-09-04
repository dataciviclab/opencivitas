SELECT
  normalize_string("codice_indicatore") AS codice_indicatore,
  normalize_string("descrizione") AS descrizione,
  normalize_string("tipo") AS tipo,
  normalize_string("categoria") AS categoria,
  normalize_string("funzione") AS funzione,
  cast_int("ordine") AS ordine,
  cast_int("anno") AS anno,
  normalize_string("ambito") AS ambito
FROM raw_input
WHERE normalize_string("codice_indicatore") IS NOT NULL

