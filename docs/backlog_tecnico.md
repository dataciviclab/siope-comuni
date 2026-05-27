# Backlog tecnico

## F5 - Validita' temporale con pivot al 31 dicembre

I join anagrafici usano:

```sql
make_date(anno, 12, 31)
```

come data di validita' per l'anno.

Effetto:

- scelta metodologica semplice e stabile per la v1
- da rivalutare se emergono enti con transizioni infra-annuali rilevanti

## F6 - [RISOLTO] codice_col7 = codice_provincia

Rinominato e documentato:

- `codice_col6` → `codice_istat_comune` (codice ISTAT 3 cifre progressivo per provincia)
- `codice_col7` → `codice_provincia` (match 110/110 con `ANAG_REG_PROV`)
- `codice_col8` → `popolazione` (residenti al momento dello snapshot)

Il dato provincia e' ora disponibile nei mart tramite join con `anag-reg-prov`.
Vedi commit `feat/align-mart-cross-year-hierarchy`.
