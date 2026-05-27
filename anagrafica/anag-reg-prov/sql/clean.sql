select
    trim(column0) as area_geografica,
    trim(column1) as codice_regione,
    trim(column2) as regione,
    trim(column3) as codice_provincia,
    trim(column4) as provincia
from raw_input;
