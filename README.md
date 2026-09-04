# OpenCivitas Intelligence — FSC x servizi dei comuni italiani, aperti e interrogabili

**Questo comune riceve X dal FSC, performa Y sui servizi: c'e coerenza?**

OpenCivitas Intelligence incrocia i dati della finanza comunale (FSC — Fondo di Solidarieta Comunale) con gli indicatori di servizio dei comuni italiani. Il risultato e un quadro chiaro su come i soldi pubblici si traducano in servizi reali, comune per comune.

## Cosa contiene

| | |
|---|---|
| **Comuni coperti** | ~6.600 (su ~7.900 totali) |
| **Periodo finanza** | 2017 — 2025 |
| **Periodo indicatori** | 2015 — 2022 |
| **Ambiti indicatori** | 7 (Rifiuti, Istruzione, Sociale, Viabilita, Amministrazione, ...) |
| **Indicatori core** | 13 (performance + contesto) |

## Esempi di domande

- **Il Comune di Roma riceve piu FSC pro-capite rispetto a Milano? E sui servizi come performa?**
- **Quali regioni hanno la miglior coerenza tra spesa e livello servizi?**
- **Come e cambiata la raccolta differenziata negli ultimi anni?**
- **Quali comuni sono piu efficienti (servizi alti, spesa bassa)?**
- **Il fondo perequativo compensa davvero le disuguaglianze?**

## Tre modi per accedere ai dati

### 1. Via MCP (toolkit del Lab)

I dataset sono esposti dal server MCP centralizzato del Lab:

```sql
-- Capacita fiscale pro-capite dei comuni (2025)
SELECT comune, capacita_fiscale_procapite
FROM opencivitas_fsc_rso
WHERE anno = 2025
ORDER BY capacita_fiscale_procapite DESC;
```

Per le tabelle mart, usa il parametro `table=mart_compose_comuni`.

**Tool disponibili**: `toolkit_dataset` (find, overview), `toolkit_query` (SQL su clean/mart).

### 2. Via DuckDB diretto

```python
import duckdb
duckdb.sql("""
    SELECT comune, capacita_fiscale_procapite
    FROM read_parquet('gs://dataciviclab-clean/opencivitas/opencivitas_fsc_rso/*_clean.parquet')
    WHERE anno = 2025
    ORDER BY capacita_fiscale_procapite DESC
""").show()
```

### 3. Via download parquet

Bucket pubblici:
- Clean: `gs://dataciviclab-clean/opencivitas/`
- Mart: `gs://dataciviclab-mart/opencivitas/`

## Dashboard

Una dashboard Streamlit e inclusa nel repo per esplorare i dati interattivamente:

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Pagine: Mappa Italia, Profilo Comune, Classifiche, Trend, Indicatori, SQL Explorer.

## Partecipa

- **Hai una domanda sui dati?** Apri una [Discussion](https://github.com/dataciviclab/opencivitas-intelligence/discussions)
- **Vuoi contribuire?** Vedi [come contribuire al Lab](https://github.com/dataciviclab/dataciviclab/blob/main/docs/come-contribuire.md)

Questo progetto fa parte di [DataCivicLab](https://github.com/dataciviclab).
