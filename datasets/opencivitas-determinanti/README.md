# opencivitas-determinanti

**Spesa standard, spesa storica e performance scores dei comuni italiani (2017-2023)**

## Cosa fa

Converte i file RDF XML del portale OpenCivitas in un dataset wide utilizzabile:
- Spesa standard vs storica per comune
- Livello servizi e spesa (0-10)
- Coordinate performance e quadrant
- Determinanti del fabbisogno standard

## Uso

```bash
# Download + convert per un anno
python preprocess.py 2022 raw_input.csv

# Pipeline toolkit
# clean → wide + join enti
# mart → fascia popolazione + etichetta quadrante
```

## Fonte

[OpenCivitas](https://www.opencivitas.it/portale/open-data) — CC BY 4.0
