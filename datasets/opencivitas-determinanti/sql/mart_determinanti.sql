-- mart_determinanti.sql — Benchmarking performance comuni
--
-- Questo mart arricchisce il clean con popolazione derivata, fascia e quadrant.
--
-- NOTE:
-- - `det_popolazione` (F_POP_C) è un INDICE demografico, non la popolazione reale
-- - La popolazione reale si calcola da: spesa_standard / spesa_standard_procapite
-- - `provincia` è codice ISTAT dal RDF (es. "100" = Firenze)

WITH base AS (
  SELECT *,
    -- Popolazione reale derivata dalla spesa standard
    CASE
      WHEN spesa_standard_procapite > 0 AND spesa_standard > 0
        THEN ROUND(spesa_standard / spesa_standard_procapite, 0)
      ELSE NULL
    END AS popolazione
  FROM clean_input
),
enriched AS (
  SELECT
    *,
    -- Fascia popolazione (usa popolazione derivata, NON det_popolazione)
    CASE
      WHEN popolazione IS NULL THEN '00_sconosciuta'
      WHEN popolazione < 1000 THEN '01_micro <1k'
      WHEN popolazione < 5000 THEN '02_piccolo 1-5k'
      WHEN popolazione < 15000 THEN '03_medio 5-15k'
      WHEN popolazione < 50000 THEN '04_grande 15-50k'
      ELSE '05_metro 50k+'
    END AS fascia_popolazione,
    -- Quadrant label
    CASE
      WHEN flag_non_valutabile = 1 THEN 'non_valutabile'
      WHEN flag_spesa_su_servizi_su = 1 THEN 'spesa_su_servizi_su'
      WHEN flag_spesa_su_servizi_giu = 1 THEN 'spesa_su_servizi_giu'
      WHEN flag_spesa_giu_servizi_giu = 1 THEN 'spesa_giu_servizi_giu'
      WHEN flag_spesa_giu_servizi_su = 1 THEN 'spesa_giu_servizi_su'
      ELSE NULL
    END AS quadrante
  FROM base
)
SELECT
  anno,
  username,
  comune,
  provincia,
  regione,
  regione_istat_cod,
  -- Popolazione (derivata)
  popolazione,
  -- Spesa
  spesa_standard,
  spesa_standard_procapite,
  spesa_storica,
  spesa_storica_procapite,
  rapporto_standard_storico,
  -- Performance
  livello_servizi,
  livello_spesa,
  coord_servizi,
  coord_spesa,
  -- Quadrant
  quadrante,
  flag_spesa_su_servizi_su,
  flag_spesa_su_servizi_giu,
  flag_spesa_giu_servizi_giu,
  flag_spesa_giu_servizi_su,
  flag_non_valutabile,
  -- Costo lavoro
  costo_lavoro_procapite,
  dipendenti_x1000ab,
  diff_servizi_pct,
  -- Determinanti (indici demografici, NON valori assoluti)
  det_popolazione AS idx_contesto_pop,
  det_densita AS idx_densita,
  det_ultra_75 AS idx_ultra_75,
  det_pop_straniera AS idx_pop_straniera,
  det_pop_15_64 AS idx_pop_15_64,
  det_pop_65_74 AS idx_pop_65_74,
  det_deprivazione AS idx_deprivazione,
  det_pendolari AS idx_pendolari,
  det_immobili AS idx_immobili,
  det_fattore_contesto AS idx_fattore_contesto,
  -- Fascia
  fascia_popolazione,
  -- Join quality
  join_enti_ok
FROM enriched
ORDER BY regione, provincia, comune
