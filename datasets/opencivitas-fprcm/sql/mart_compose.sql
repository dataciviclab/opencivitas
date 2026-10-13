-- mart_compose.sql — metriche derivate FPRCM
--
-- Il pivot e il join geografico sono già stati fatti nel CLEAN.
-- Qui aggiungiamo solo le metriche procapite derivate.

select
  anno,
  username,
  ente, tipologia_ente, provincia, regione, provincia_istat_cod, regione_istat_cod,
  popolazione,
  capacita_fiscale,
  fabbisogni_standard,
  contributo_fondamentali_prov,
  totale_contributi_fondi_correnti,
  join_enti_ok,
  case
    when popolazione is not null and popolazione <> 0
      then capacita_fiscale / popolazione
    else null
  end as capacita_fiscale_procapite,
  case
    when popolazione is not null and popolazione <> 0
      then fabbisogni_standard / popolazione
    else null
  end as fabbisogni_standard_procapite,
  case
    when popolazione is not null and popolazione <> 0
      then contributo_fondamentali_prov / popolazione
    else null
  end as contributo_fondamentali_procapite
from clean_input
order by regione, provincia, ente
