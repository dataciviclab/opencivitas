# Notes

## Tecnico

- file sorgente: XLSX diretto dal portale Liferay (non ZIP), `Metadati_Enti_FPRCM_2026.xlsx`
- foglio: `anagrafica_enti_FPRCM2026` (88 righe)
- colonne viste: CODICE_MINISTERO_INTERNO, USERNAME, ENTE, ENTE_TIPOLOGIA,
  REGIONE_DES, PROVINCIA_DES, COMUNE_ISTAT_COD, COMUNE_CATASTO_COD,
  ANNO_INIZIO, ANNO_FINE, PROVINCIA_ISTAT_COD, REGIONE_ISTAT_COD, DENOMINAZIONE_PROV
- 2 righe rumore `ZZ999TIP001/002` (ENTE_TIPOLOGIA='TIPOLOGIA ENTE') → filtrate nel clean
- enti: 86 reali (73 PROVINCIA, 10 CITTAMETROPOLITANA, 3 PROVINCIAMONTANA)

## Analitico

- support dataset per `opencivitas-fprcm` (fondo solidarietà province/CM)
- anagrafica disgiunta da `opencivitas_fsc_enti_rso` (comuni RSO): stesso formato
  username SIF ma entità diverse, nessuna sovrapposizione
- la serie è stabile 2022-2026 (88/88 enti invariati) → single-year 2026 basta

## Cautele

- perimetro solo RSO (Sicilia e Sardegna escluse, come il FSC comuni)
- foglio XLSX con nome year-specific: bumpare `sheet_name` se si estende l'anagrafica
