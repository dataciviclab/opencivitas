# Decisioni tecniche

## Join su username

Tutti i dataset si uniscono sul campo `username` (codice ente OpenCivitas). Non esiste un ISTAT code universale: l'anagrafica enti fornisce `regione_istat_cod` ma non un codice comunale standard.

## Esclusione 2020

L'anno 2020 non e presente nei dati OpenCivitas per indicatori e determinanti. Il FSC parte dal 2017. Gli anni di sovrapposizione (2017, 2018, 2021, 2022) sono i 4 anni in cui e possibile incrociare finanza e servizi.

## Normalizzazione EAV

Indicatori e FSC sono in formato EAV (Entity-Attribute-Value). Il clean.sql pivota in wide: una riga per comune/anno con colonne per ogni metrica. Questo rende le query piu semplici e le dashboard piu veloci.

## Determinanti: popolazione reale vs indice

La colonna `F_POP_C` nei determinanti e un indice, non la popolazione reale. La popolazione reale viene calcolata come `spesa_standard / spesa_standard_procapite`.

## Support dataset

Due dataset di supporto (`opencivitas-fsc-enti-rso` e `opencivitas-glossario`) vengono eseguiti prima dei dataset principali. Sono anagrafiche che arricchiscono i dati grezzi con geografia e metadati.
