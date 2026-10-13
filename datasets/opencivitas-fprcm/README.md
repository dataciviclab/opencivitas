# opencivitas-fprcm

**Fondo di Solidarietà per le Province e Città Metropolitane (FPRCM)** — 86 enti
RSO, 2022→2026.

Gemello provinciale di `opencivitas-fsc-rso` (che copre i comuni RSO): stessa
fonte (portale OpenCivitas), stessa shape long `USERNAME;componente;valore`,
stesso trattamento posizionale. Qui però il riparto è a provincia/CM: 88 enti ×
19 componenti di calcolo del fondo.

- **Dati**: CSV diretti dal portale Liferay (URL con UUID per anno, `url_suffix_by_year`)
- **Support**: `opencivitas-fprcm-enti` — anagrafica enti (denominazione, tipologia, ISTAT)
- **Mart**: `mart_compose_province` — wide + metriche procapite (capacità fiscale,
  fabbisogni standard, contributo fondamentali)

Colonne chiave del mart: `ente`, `tipologia_ente`, `popolazione`,
`capacita_fiscale`, `fabbisogni_standard`, `contributo_fondamentali_prov`,
`totale_contributi_fondi_correnti`, più le versioni procapite.

Fonte: [OpenCivitas — Open Data](https://www.opencivitas.it/portale/open-data),
sezione "Riparto fondi".
