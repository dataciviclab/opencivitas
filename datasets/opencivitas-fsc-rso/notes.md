# Notes

## Tecnico

- source A: CSV diretti dal portale Liferay (`http_file`, URL con UUID in dataset.yml)
  - 2017-2021: serie originale `{year}_VAR_FSC_1` (identica ai vecchi ZIP docs,
    177687 righe — verificato). La serie revisionata `{year}_VAR_FSC_1_2022` ha
    il set componenti 2022 (164525 righe): non usarla per gli anni storici.
  - 2022-2025: `{year}_VAR_FSC_1_{year}`
  - 2026+: `{year}_VAR_FSC_1_{year}_IT.csv`
- UUID negli URL: se Sogei ricarica un file, l'URL cambia — recuperare il nuovo
  dall'inventario catalog-watch (`out/so/inventory.parquet` / `registry/catalog.json`)
- CSV con `;` come delimitatore e `,` come separatore decimale, header presente (filtrato dal clean via `componente IN (...)`)
- shape long, una riga per componente di calcolo del fondo
- source B: ZIP con workbook `Metadati_Enti_FSC_2025.xlsx` (support `opencivitas_fsc_enti_rso`)
- source B: sheet `anagrafica_enti2025` (sheet_name statico, non templabile con {year})
- chiave di join comune: `USERNAME`
- 2019: mai pubblicato dalla fonte (gap confermato su docs e portale)
- colonne raw per posizione (col0=USERNAME, col1=nome, col2=valore)
  - 2022-2024: VAR_FSC_NAME / VAR_FSC_VAL
  - 2025+: Componenti di calcolo del fondo / Valore
- il clean SQL gestisce entrambi i formati (posizionale)
- migrazione 2026-10: da `type: script` (preprocess.py, ZIP docs) a `http_file`
  per-anno sul portale — regressione verificata via run records `_runs/`
  (raw/clean/mart identici ai run precedenti basati su docs)

## Anni

| Anno | Fonte (portale) | Colonne raw |
|:----:|-----------------|-------------|
| 2017-2021 | `{year}_VAR_FSC_1` (serie originale) | USERNAME, VAR_FSC_NAME, VAR_FSC_VAL |
| 2022-2024 | `{year}_VAR_FSC_1_{year}` | USERNAME, VAR_FSC_NAME, VAR_FSC_VAL |
| 2025 | `{year}_VAR_FSC_1_{year}` | USERNAME, Componenti di calcolo del fondo, Valore |
| 2026 | `{year}_VAR_FSC_1_{year}_IT.csv` | USERNAME, Componenti di calcolo del fondo, Valore |

## Analitico

- sei componenti chiave FSC: POPOLAZIONE, CAPACITA_FISCALE, FONDO_PEREQUATIVO,
  DOTAZIONE_FINALE_FSC, IMU_TASI_STANDARD, TOTALE_RISORSE_STORICHE
- `FONDO_PEREQUATIVO` è la metrica di partenza più leggibile
- source B (enti) vive in `support_datasets/` ed è dataset fisso (2025)
- il mart arricchito (`mart_compose_comuni`) include metriche procapite

## Cautele

- perimetro solo RSO (~6.570 comuni): non usare "tutti i comuni italiani"
- Sicilia e Sardegna escluse (hanno solo componente storica)
- il numero di comuni varia leggermente tra anni (~±8)
- support anagrafica è single-year 2025: sul 2026 il join è 100% (6572/6572);
  se dovesse scendere, opzioni reali = bump single-year del support oppure
  multi-anno via placeholder `.clean` + QUALIFY dedup (il placeholder `.mart`
  è single-year per design, `sheet_name` non è templabile)
