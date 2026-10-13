select distinct
  username,
  denominazione,
  tipologia_ente,
  provincia,
  regione,
  provincia_istat_cod,
  regione_istat_cod
from clean_input
where username is not null
