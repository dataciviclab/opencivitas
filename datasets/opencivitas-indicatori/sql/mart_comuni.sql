-- mart_comuni.sql — Pivot indicatori per comune × anno + benchmark
--
-- Input: clean_input (una riga per comune × anno × indicatore)
-- Output: una riga per comune × anno con:
--   - 15 indicatori core pivottati da EAV a wide
--   - Geografia da enti-rso
--   - Percentili e fasce per le metriche chiave

WITH pivotted AS (
    SELECT
        username,
        anno,
        -- Performance: rifiuti
        MAX(CASE WHEN indicatore LIKE 'RACC_DIFFER_PERC%' THEN valore_num END) AS raccolta_differenziata_pct,
        MAX(CASE WHEN indicatore LIKE 'RIFIUTI_URBANI_P_KG%' THEN valore_num END) AS rifiuti_kg_proab,
        -- Performance: istruzione
        MAX(CASE WHEN indicatore LIKE 'M_REFEZIONE_PERC%' THEN valore_num END) AS mensa_scolastica_pct,
        MAX(CASE WHEN indicatore LIKE 'M_SPAZI_TOT_P%' THEN valore_num END) AS mq_scuole_per_ab,
        MAX(CASE WHEN indicatore LIKE 'M_TRASPORTO_UTENTI_PERC%' THEN valore_num END) AS trasporti_scuola_pct,
        -- Performance: sociale/nido
        MAX(CASE WHEN indicatore LIKE 'SUPERF_TOT_C%' THEN valore_num END) AS nido_mq_per_utente,
        -- Performance: viabilita
        MAX(CASE WHEN indicatore LIKE 'ISTAT_GENER_STRADE_INTER_KM%' THEN valore_num END) AS strade_interne_km,
        -- Performance: polizia/locale
        MAX(CASE WHEN indicatore LIKE 'INCIDENTI_PM%' THEN valore_num END) AS incidenti_per1000ab,
        -- Performance: amministrazione
        MAX(CASE WHEN indicatore LIKE 'DIPENDENTI_X1000AB%' AND ambito = 'amministrazione' THEN valore_num END) AS dipendenti_per1000ab,
        -- Contesto
        MAX(CASE WHEN indicatore LIKE 'REDDITO_MEAN%' THEN valore_num END) AS reddito_medio,
        MAX(CASE WHEN indicatore LIKE 'INCID_POP_STRA_MEAN%' THEN valore_num END) AS pop_straniera_pct,
        MAX(CASE WHEN indicatore LIKE 'INCID_OLTRE_75_MEAN%' THEN valore_num END) AS ultra75enni_pct,
        MAX(CASE WHEN indicatore LIKE 'IND_POP02_SU_POPTOT_PCT%' THEN valore_num END) AS bambini0_2_pct,
        MAX(CASE WHEN indicatore LIKE 'INCIDENZA_POP_3_14_PERC%' THEN valore_num END) AS pop_3_14_pct
    FROM clean_input
    WHERE tipo_indicatore = 'IND'
      AND valore_num IS NOT NULL
    GROUP BY username, anno
),
with_geo AS (
    SELECT
        p.*,
        e.denominazione AS comune,
        e.provincia,
        e.regione,
        e.regione_istat_cod,
        f.popolazione
    FROM pivotted p
    LEFT JOIN read_parquet('{support.opencivitas_fsc_enti_rso.mart}') e
        ON p.username = e.username
    LEFT JOIN read_parquet('{root}/data/mart/opencivitas_fsc_rso/*/mart_compose_comuni.parquet', union_by_name=true) f
        ON p.username = f.username AND p.anno = f.anno
),
with_benchmark AS (
    SELECT
        *,
        -- Percentili (per confronti)
        ROUND(percent_rank() OVER (PARTITION BY anno ORDER BY raccolta_differenziata_pct), 4) AS pct_raccolta,
        ROUND(percent_rank() OVER (PARTITION BY anno ORDER BY mensa_scolastica_pct), 4) AS pct_mensa,
        ROUND(percent_rank() OVER (PARTITION BY anno ORDER BY nido_mq_per_utente), 4) AS pct_nido,
        ROUND(percent_rank() OVER (PARTITION BY anno ORDER BY incidenti_per1000ab), 4) AS pct_incidenti,
        -- Media nazionale (per delta)
        ROUND(AVG(raccolta_differenziata_pct) OVER (PARTITION BY anno), 2) AS media_naz_raccolta,
        ROUND(AVG(mensa_scolastica_pct) OVER (PARTITION BY anno), 2) AS media_naz_mensa,
        -- Fascia popolazione (da FSC popolazione)
        CASE
            WHEN popolazione IS NULL THEN 'N/D'
            WHEN popolazione < 1000 THEN '01_micro <1k'
            WHEN popolazione < 5000 THEN '02_piccolo 1-5k'
            WHEN popolazione < 15000 THEN '03_medio 5-15k'
            WHEN popolazione < 50000 THEN '04_grande 15-50k'
            ELSE '05_metro 50k+'
        END AS fascia_popolazione,
        -- Conteggio indicatori presenti
        (
            (CASE WHEN raccolta_differenziata_pct IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN mensa_scolastica_pct IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN mq_scuole_per_ab IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN trasporti_scuola_pct IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN nido_mq_per_utente IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN strade_interne_km IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN incidenti_per1000ab IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN dipendenti_per1000ab IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN reddito_medio IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN pop_straniera_pct IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN ultra75enni_pct IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN bambini0_2_pct IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN pop_3_14_pct IS NOT NULL THEN 1 ELSE 0 END)
        ) AS n_indicatori_presenti
    FROM with_geo
)
SELECT
    *,
    -- Delta vs media nazionale
    CASE
        WHEN media_naz_raccolta > 0
        THEN ROUND((raccolta_differenziata_pct - media_naz_raccolta) / media_naz_raccolta * 100, 1)
    END AS delta_raccolta_vs_media_naz
FROM with_benchmark
WHERE comune IS NOT NULL
ORDER BY regione, provincia, comune, anno
