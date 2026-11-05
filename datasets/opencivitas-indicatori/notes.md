# opencivitas-indicatori — Note

## Origine

Fonte: [OpenCivitas](https://www.opencivitas.it/portale/open-data) (ANCI/Sogei).
CSV in formato EAV (USERNAME;Indicatore;Valore;Anomalia;Privacy), scaricati
direttamente dal portale Liferay (URL con UUID). Il vecchio `docs.opencivitas.it`
è dismesso.

## Due ere

- **2009-2013**: formato wide (spesa storica, fabbisogni), chiave = COMUNE_CAT_COD
- **2017-2022**: formato EAV (indicatori e determinanti), chiave = USERNAME
- **2023**: naming nuovo sul portale Liferay (sigle estese `AMMINISTR`/`TERR_VIAB`,
  suffisso `_01_IT`) — gestito nel preprocess via la mappa `PORTAL`; schema CSV
  identico agli anni precedenti

Questo candidate copre la **seconda era**: 7 ambiti × 6 anni (2017-2023, salto 2020) in formato EAV.
(2015-2016 fuori copertura: il portale parte dal 2017.)

## Pipeline

```
preprocess.py {year} raw_input.csv
  → scarica i 7 CSV ambito dal portale, unisce con colonna ambito
  
clean.sql
  → normalizza username, anno, indicatore
  → converte valore (decimale , → .)
  → LEFT JOIN enti su username (denominazione, provincia, regione)
  → LEFT JOIN glossario su (codice_indicatore, anno, ambito)
  
mart_comuni
  → unisce i vecchi mart.sql (join comuni_master) + mart_benchmark
  → aggiunge codice_istat + benchmark (media nazionale/regionale, percentile, fascia)

mart_sintesi
  → ex mart_sintesi_territoriale (rinominato)
  → statistiche per provincia/regione/nazionale

mart_trend (opzionale)
  → CAGR indicatori su 6 anni (glob multi-anno)
```

## Support dataset

| Nome | Ruolo | Note |
|---|---|---|
| `opencivitas_fsc_enti_rso` | Anagrafica enti | username → denominazione/regione |
| `opencivitas_glossario` | Dizionario | 3 fogli: IND + DET + COD |
| `comuni_master` | Golden record | codice_istat, catastale |

## Qualità

- Drop 10-12%: valori testuali attesi (descrizioni, codici anomalia)
- Enti riconosciuti: 99,8%
- Glossario coperto: ~100% (eccezione: `servizi_totali` 2018, metadati non pubblicati dalla fonte)
- Match ISTAT: 95-98% (crescente da 2017 a 2023, media ~96,5%)
- Duplicati: 0 (sulla chiave username+anno+ambito+indicatore)

## Placeholder toolkit

- `{root}` → output root (es. `.../dataset-incubator/out`)
- `{year}` → anno corrente del candidate
- `{support.*.mart}` → mart del support dataset
