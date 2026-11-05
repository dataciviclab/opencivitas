# b_enti

Source `B` - metadati enti FSC 2025 per il mapping `USERNAME -> comune`.

## Stato

`incubating` - sorgente interna del candidate
[opencivitas-fsc-rso](../../README.md), nata durante il lavoro su
[#85](https://github.com/dataciviclab/dataset-incubator/issues/85).

## Uso previsto

Decodificare la chiave tecnica `USERNAME` presente nei file OpenCivitas FSC 2025 e
agganciare:

- denominazione comune
- provincia
- regione

## Dataset

Fonte principale:

- OpenCivitas / Sogei, metadati enti FSC 2025
- portale Liferay OpenCivitas (XLSX diretto, URL con UUID):
   `https://www.opencivitas.it/portale/documents/20118/0/Metadati_Enti_FSC_2025/ce487ca0-53ee-5162-7df9-24307a773af4`
- workbook: `Metadati_Enti_FSC_2025.xlsx`
- sheet: `anagrafica_enti2025`

> Nota: fino a ottobre 2026 la fonte era lo ZIP
> `http://docs.opencivitas.it/Metadati_Enti_FSC_2025_xlsx.zip`. Il dominio
> `docs.opencivitas.it` è stato dismesso; la fonte è migrata al portale.

## Output minimo atteso

- `clean` sul workbook XLSX
- `mart` con una riga per `USERNAME`
- mapping riusabile per il join con `opencivitas-fsc-rso`

## Ruolo nel candidate

- fornire il mapping di base per il join con il source `A`
- evitare che il candidate principale resti bloccato su chiavi tecniche non
  leggibili
