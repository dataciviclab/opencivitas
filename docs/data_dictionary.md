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
