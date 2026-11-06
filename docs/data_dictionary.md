# Dizionario dati

## opencivitas_fsc_enti_rso (support)

Anagrafica enti. Un record per ente.

| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| username | VARCHAR | Codice ente (chiave primaria) |
| denominazione | VARCHAR | Nome dell'ente |
| provincia | VARCHAR | Sigla provincia |
| regione | VARCHAR | Nome regione |
| regione_istat_cod | VARCHAR | Codice ISTAT regione |

## opencivitas_glossario (support)

Dizionario indicatori. Un record per indicatore/anno/ambito.

| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| codice_indicatore | VARCHAR | Codice univoco indicatore |
| descrizione | VARCHAR | Nome dell'indicatore |
| tipo | VARCHAR | IND (indicatore) o DET (determinante) |
| categoria | VARCHAR | Categoria tematica |
| funzione | VARCHAR | Funzione di valutazione |
| anno | INTEGER | Anno di riferimento |
| ambito | VARCHAR | Ambito tematico |

## opencivitas_determinanti

Benchmarking comuni: spesa standard vs storica, performance, quadrante.

| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| username | VARCHAR | Codice ente |
| comune | VARCHAR | Nome comune |
| regione | VARCHAR | Nome regione |
| popolazione | FLOAT | Popolazione reale (calcolata) |
| spesa_standard_procapite | FLOAT | Spesa standard pro-capite |
| spesa_storica_procapite | FLOAT | Spesa storica pro-capite |
| livello_servizi | FLOAT | Indice livello servizi |
| livello_spesa | FLOAT | Indice livello spesa |
| quadrante | VARCHAR | A (alto servizio, bassa spesa) / B / C / D |
| fascia_popolazione | VARCHAR | Fascia demografica |
| livello_territoriale | VARCHAR | `comune` / `regione` / `nazionale` / `altro` — solo nel **clean**; il mart è solo comuni |

## opencivitas_fsc_rso

FSC (Fondo di Solidarieta Comunale) multi-anno.

| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| username | VARCHAR | Codice ente |
| comune | VARCHAR | Nome comune |
| anno | INTEGER | Anno di riferimento |
| popolazione | FLOAT | Popolazione |
| capacita_fiscale | FLOAT | Capacita fiscale |
| fondo_perequativo | FLOAT | Fondo perequativo |
| dotazione_finale_fsc | FLOAT | Dotazione Finanziaria FSC |
| capacita_fiscale_procapite | FLOAT | Capacita fiscale pro-capite |
| fondo_perequativo_procapite | FLOAT | Fondo perequativo pro-capite |
| dotazione_finale_fsc_procapite | FLOAT | Dotazione FSC pro-capite |
| livello_territoriale | VARCHAR | `comune` / `regione` / `nazionale` / `altro` — solo nel **clean**; il mart è solo comuni |

## opencivitas_indicatori

Indicatori di servizio multi-ambito, formato EAV.

| Colonna | Tipo | Descrizione |
|---------|------|-------------|
| username | VARCHAR | Codice ente |
| anno | INTEGER | Anno di riferimento |
| ambito | VARCHAR | Ambito tematico |
| indicatore | VARCHAR | Codice indicatore |
| valore_num | FLOAT | Valore numerico |
| descrizione_indicatore | VARCHAR | Nome indicatore |
| tipo_indicatore | VARCHAR | IND o DET |
| categoria_indicatore | VARCHAR | Categoria |
| funzione_indicatore | VARCHAR | Funzione di valutazione |
| denominazione | VARCHAR | Nome ente |
| provincia | VARCHAR | Sigla provincia |
| regione | VARCHAR | Nome regione |
| livello_territoriale | VARCHAR | `comune` / `regione` / `nazionale` / `altro` — solo nel **clean**; il mart è solo comuni |

## Livello territoriale (clean vs mart)

Le fonti OpenCivitas includono, insieme ai comuni, **righe aggregate** (le 15
regioni RSO e ITALIA, più alcune aree). Per evitare doppi conteggi:

- il **clean** conserva tutte le righe della fonte e le marca con
  `livello_territoriale` (`comune` / `regione` / `nazionale` / `altro`);
- i **mart** `*_comuni` / `*_determinanti` filtrano `livello_territoriale = 'comune'`
  → contengono **solo comuni** (nessuna regione o ITALIA).

Per i totali regionali/nazionali usare le righe aggregate del clean (valori
ufficiali della fonte), non sommare i mart.

**Comuni senza geografia**: alcuni comuni non si agganciano all'anagrafica
(single-year 2025) — fusioni/abolizioni, oppure username troncati nella fonte
RDF. Nel clean/mart hanno `join_enti_ok = false`; i determinanti recuperano i
troncati via chiave normalizzata (`049SIF11OP` → `NA049SIF11OP`).
