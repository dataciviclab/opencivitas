# Fonti dati

## OpenCivitas (ANCI / Sogei)

- **Sito**: https://docs.opencivitas.it
- **Dati finanziari (FSC)**: ZIP CSV con delimitatore `;`, un file per anno. Copre 2017-2025.
- **Indicatori di servizio**: 7 ZIP per anno (uno per ambito: Rifiuti, Istruzione, Sociale, Viabilita, Amministrazione, Territorio, Finanza Locale). Copre 2015-2022 (no 2020).
- **Determinanti**: RDF XML trasformato in CSV wide. Benchmarking spesa standard vs storica, performance, quadrante. Copre 2015-2022.
- **Metadati enti**: XLSX con anagrafica enti (username, denominazione, provincia, regione).
- **Glossario indicatori**: XLSX con dizionario indicatori (codice, descrizione, tipo, categoria, funzione, ambito).

## Licenza dati

I dati OpenCivitas sono pubblici e scaricabili liberamente dal portale ANCI. Il codice SQL e di trasformazione in questo repo e distribuito con licenza MIT (vedi LICENSE).

## Qualita dei dati

- **Formati decimali misti**: 2015-2016 usano il punto come separatore decimale, 2017-2022 la virgola. Il clean.sql gestisce entrambi.
- **Anno 2020 mancante**: L'anno 2020 non e presente nei dati OpenCivitas per indicatori e determinanti.
- **Aggregati regionali**: Alcuni record hanno provincia vuota (aggregati regionali). La dashboard li filtra.
- **Join su username**: Il campo `username` e la chiave primaria per unire enti, FSC e indicatori.
