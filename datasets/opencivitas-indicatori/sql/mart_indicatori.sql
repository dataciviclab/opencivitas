-- mart_indicatori.sql — Aggregato per anno × indicatore con statistiche
--
-- Solo indicatori (IND), no determinanti (DET) o codici anomalia (COD).
-- Una riga per (anno, ambito, indicatore) con statistiche.

SELECT
    anno,
    ambito,
    indicatore,
    COUNT(*) as n_comuni,
    ROUND(AVG(valore_num), 4) as media,
    ROUND(MEDIAN(valore_num), 4) as mediana,
    ROUND(STDDEV(valore_num), 4) as dev_std,
    ROUND(MIN(valore_num), 4) as minimo,
    ROUND(MAX(valore_num), 4) as massimo,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY valore_num), 4) as q25,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY valore_num), 4) as q75
FROM clean_input
WHERE valore_num IS NOT NULL
  AND tipo_indicatore = 'IND'
GROUP BY anno, ambito, indicatore
ORDER BY anno, ambito, indicatore


