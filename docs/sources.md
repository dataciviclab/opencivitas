# Fonti dati

## OpenCivitas (ANCI / Sogei)

- **Sito**: https://www.opencivitas.it/portale/open-data (portale Liferay; il vecchio `docs.opencivitas.it` è dismesso)
- **Dati finanziari (FSC)**: CSV con delimitatore `;`, un file per anno. Copre 2017-2026.
- **Indicatori di servizio**: CSV per anno (uno per ambito: Rifiuti, Istruzione, Sociale, Viabilita, Amministrazione, Territorio, Servizi totali). Copre 2017-2023 (no 2020).
- **Determinanti**: RDF XML trasformato in CSV wide. Benchmarking spesa standard vs storica, performance, quadrante. Copre 2017-2023.
- **Metadati enti**: XLSX con anagrafica enti (username, denominazione, provincia, regione).
- **Glossario indicatori**: XLSX con dizionario indicatori (codice, descrizione, tipo, categoria, funzione, ambito). Copre 2017-2023.

## Licenza dati

I dati OpenCivitas sono pubblici e scaricabili liberamente dal portale ANCI. Il codice SQL e di trasformazione in questo repo e distribuito con licenza MIT (vedi LICENSE).

## Qualita dei dati

- **Formati decimali misti**: i valori decimali con virgola sono normalizzati a punto nel preprocess.
- **Anno 2020 mancante**: L'anno 2020 non e presente nei dati OpenCivitas per indicatori e determinanti.
- **2015-2016 fuori copertura**: il portale nuovo copre dal 2017; 2015-2016 sono usciti dalla pipeline (dato storico congelato su GCS).
- **Glossario 2018 TOT mancante**: il metadati `servizi_totali` 2018 non è pubblicato dalla fonte (né su portale né su Wayback).
- **Aggregati regionali**: Alcuni record hanno provincia vuota (aggregati regionali). La dashboard li filtra.
- **Join su username**: Il campo `username` e la chiave primaria per unire enti, FSC e indicatori.
