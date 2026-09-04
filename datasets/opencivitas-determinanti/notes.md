# opencivitas-determinanti — Note

## Root cause fixate

1. **`F_POP_C` NON èla popolazione** — èun indice demografico (~54). La popolazione reale si calcola da `spesa_standard / spesa_standard_procapite`
2. **`provincia` ècodice ISTAT** (es. "100"=FI) — il RDF non ha i nomi delle province
3. **Formato decimale misto** — 2015/2022 usano il punto, 2017-2019 la virgola. Fix: normalizzazione nel preprocess.py
4. **`normalize_italian_number`** trattava il punto come separatore migliaia → usare `TRY_CAST` diretto dopo normalizzazione

## Origine

Fonte: [OpenCivitas](https://www.opencivitas.it/) (ANCI/Sogei/SOSE).
File RDF XML dal portale open data — non i CSV indicatori (EAV).

## Cosa contiene

Il file RDF del TOT (servizi totali aggregati) contiene per ogni comune:

| Categoria | Colonne | Descrizione |
|-----------|---------|-------------|
| **Spesa standard** | `FST_RIPROPORZIONATO_BI` / `_PROAB` | Quanto il comune dovrebbe spendere (€ totale / € per abitante) |
| **Spesa storica** | `SPESA_STORICA` / `_PROAB` | Quanto il comune ha speso realmente |
| **Performance** | `POSIZIONE_OUTPUT_PERC_TOT` / `_SPESA_PERC_TOT` | Livello servizi e spesa (0-10) |
| **Coordinate** | `COORD_OUT` / `COORD_SPESA` | Posizionamento performance (-5 a +5) |
| **Quadrant** | `FL_SPESA_PIU_OUT_PIU` / etc. | Quale quadrante (4 quadranti performance) |
| **Costo lavoro** | `COSTO_LAVORO_PROAB`, `DIPENDENTI_X1000AB` | Costo lavoro e dipendenti |
| **Determinanti** | `F_POP_C`, `F_DENSITA_MEAN`, etc. | Variabili che determinano il fabbisogno |

## Differenza dai CSV indicatori

| | CSV Indicatori (EAV) | RDF Determinanti (wide) |
|--|---------------------|------------------------|
| Formato | USERNAME;indicatore;valore | Wide: una riga per comune, N colonne |
| Contenuto | Valori grezzi degli indicatori | **Spesa standard, spesa storica, performance scores, determinanti** |
| Copertura | 7 ambiti + TOT | Solo TOT (aggregato) |
| Utilità | Monitoraggio singolo indicatore | **Benchmarking**: confronto standard vs storico |

## Pipeline

```
preprocess.py {year} raw_input.csv
  → scarica ZIP RDF, parse XML <vi:rig>, converte in CSV wide

clean.sql
  → normalizza colonne (cast double, NULLIF vuoti)
  → LEFT JOIN enti su username (denominazione, provincia, regione)
  → calcola rapporto_standard_storico

mart_determinanti.sql
  → aggiunge fascia_popolazione (5 classi)
  → etichetta quadrante (spesa_su/su, spesa_su/giu, etc.)
```

## Anni disponibili

| Anno | Comuni | Colonne RDF | Note |
|------|--------|-------------|------|
| 2015 | 6.694 | 90 | Primo anno disponibile |
| 2016 | 6.677 | 90 | |
| 2017 | 6.657 | 98 | Aggiunte determinanti |
| 2018 | 6.636 | 98 | |
| 2019 | 6.597 | 97 | |
| 2020 | — | — | Non disponibile (salto) |
| 2021 | 6.595 | 91 | |
| 2022 | 6.587 | 84 | Ultimo anno disponibile |

## Colonne chiave stabili (presenti in tutti gli anni)

Le 18 colonne spesa/performance sono garantite in tutti i 7 anni:
`SPESA_STORICA`, `SPESA_STORICA_PROAB`, `FST_RIPROPORZIONATO_BI`,
`FST_RIPROPORZIONATO_BI_PROAB`, `POSIZIONE_OUTPUT_PERC_TOT`,
`POSIZIONE_SPESA_PERC_TOT`, `COORD_OUT`, `COORD_SPESA`,
`DIPENDENTI_X1000AB`, `COSTO_LAVORO_PROAB`, ecc.

Le determinanti (F_*) variano tra anni per cambiamenti metodologici.

## Perimetro

- Solo RSO (~6.500-6.700 comuni)
- Sicilia e Sardegna escluse
- Il numero di comuni varia ~±8 tra anni

## Placeholder toolkit

- `{root}` → output root
- `{year}` → anno corrente
- `{support.opencivitas_fsc_enti_rso.mart}` → mart anagrafica enti
