# Notes

## Tecnico

- source: CSV diretti dal portale Liferay (`http_file`, URL con UUID in dataset.yml)
  - 2022: `2022_FPRCM_2_2023` (modulo 2 correttivo: `POPOLAZIONE_2020` → `POPOLAZIONE`,
    valori identici al modulo 1 — verificato) — usato per coerenza anni successivi
  - 2023: `2023_FPRCM_1_2023`
  - 2024: `2024_FPRCM_01_2024_IT.csv`
  - 2025: `2025_FPRCM_1_2025`
  - 2026: `2026_FPRCM_01_2026_IT.csv`
- UUID negli URL: se Sogei ricarica un file, l'URL cambia — recuperare il nuovo
  dall'inventario catalog-watch (`out/so/inventory.parquet` / `registry/catalog.json`)
- CSV con `;` come delimitatore e `,` come separatore decimale, header variabile
  tra anni (posizionale, come FSC)
- shape long, una riga per componente di calcolo del fondo
- 88 enti × 19 componenti = 1672 righe/anno, perfettamente stabili 2022→2026
- source B: anagrafica `Metadati_Enti_FPRCM_2026.xlsx` (support `opencivitas_fprcm_enti`)
- chiave di join comune: `USERNAME`

## Componenti nel clean (pivot)

| Componente | Descrizione |
|---|---|
| POPOLAZIONE | residenti |
| CAPACITA_FISCALI | capacità fiscale (plurale in tutti gli anni) |
| FABBISOGNI_STANDARD | fabbisogni standard province |
| CONTRIBUTO_FONDAMENTALI_PROV | contributo fondamentali |
| TOTALE_CONTR_FONDI_CORR_2021 | totale contributi fondi correnti 2021 |

Le altre 14 componenti (famiglia CONCORSO_NETTO_FINPUBBL_*, comma 418/439/754/838,
RIDUZIONE_69MILIONI, RISORSE_AGGIUNTIVE…) restano nel raw ma non sono pivotate nel clean v0.

## Analitico

- FPRCM = Fondo di Solidarietà per Province e Città Metropolitane — gemello
  provinciale del FSC comuni (`opencivitas-fsc-rso`)
- 86 enti RSO (73 province, 10 città metropolitane, 3 province montane);
  Sicilia e Sardegna escluse come nel FSC
- domanda civica: come il fondo ripartisce standard vs capacità fiscale tra le
  province, e quanto pesano i concorsi netti 2021
- anagrafica disgiunta da `opencivitas_fsc_enti_rso` (comuni): stesso formato
  username SIF ma entità diverse, nessuna sovrapposizione

## Cautele

- perimetro solo RSO: non usare "tutte le province italiane"
- per capire le componenti normative di un campo, il dizionario ufficiale è
  `Metadati_FPRCM_{year}.xlsx` (22 righe con formula e descrizione) — non ancora
  incorporato come support
- 2019 gap del FSC non si applica qui: la serie FPRCM parte dal 2022 senza buchi
