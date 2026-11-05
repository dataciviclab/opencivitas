# opencivitas-glossario — Note

## Origine

File XLSX di metadati dal portale Liferay OpenCivitas (URL con UUID, es. `{year}_Metadati_Ind_FC{code}_{sigla}_{n}`).
Ogni file contiene 3 fogli: Indicatori, Determinanti, Codici.

## Pipeline

```
preprocess.py {year} raw_input.csv
  → download 7 XLSX (uno per ambito)
  → estrae 3 fogli da ciascuno
  → unisce in CSV unico con colonne: codice_indicatore, descrizione, tipo, categoria, funzione, ordine, anno, ambito

clean.sql → pass-through (normalizza trim/cast)

mart.sql → pass-through (select * from clean_input)
```

## Anni

6 anni: 2017, 2018, 2019, 2021, 2022, 2023.
(2020 assente: nessun indicatore pubblicato. 2015-2016 usciti dalla copertura:
il portale nuovo parte dal 2017.)

## Note

- Fonte unica: portale Liferay OpenCivitas, XLSX diretti con URL a UUID
  (il vecchio dominio `docs.opencivitas.it` è dismesso).
- Mappa esplicita `PORTAL` anno → {ambito: "nome/uuid"} nel preprocess: i
  suffissi variano tra anni (es. TOT 2019 `_2`, TOT 2022 `_1`) e non sono
  ricostruibili da una regola unica.
- **2018 TOT mancante**: il metadati `servizi_totali` 2018 non è pubblicato
  dalla fonte (né su portale né su Wayback). In `KNOWN_MISSING` → skip con
  warning. Impatto: mancano 114 voci `servizi_totali` del 2018 → nel dataset
  `opencivitas_indicatori` le **573.728 righe `servizi_totali` 2018** restano
  senza descrizione (`join_metadati_ok=False`). 75 degli 87 indicatori TOT 2018
  esistono nel glossario sotto altri ambiti, ma il join è su
  `(codice, anno, ambito)` e non li recupera.
- 2023: XLSX dal portale con naming nuovo e sigle estese; **fogli e colonne
  diversi** dal 2022:
  - fogli `Indicatori_FC90_*` / `Det_FC90_*` (prefisso abbreviato) / `Codici_FC90_*`
  - colonne italiane (`Codice Indicatore`, `Descrizione`, `Tipo di indicatore`,
    `Funzione`, `Var Ord`) — il preprocess le mappa via `_pick` accanto al
    vecchio schema `VAR_IND_*`
- I determinanti (DET) e i codici (COD) variano per anno
- Il candidate referenzia il mart via `{root}/data/mart/opencivitas_glossario/{year}/mart_metadati.parquet`
