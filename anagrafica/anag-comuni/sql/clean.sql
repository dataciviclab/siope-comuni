select
    trim(column0) as codice_istat_comune,
    trim(column1) as denominazione_comune,
    trim(column2) as codice_provincia
from raw_input;
