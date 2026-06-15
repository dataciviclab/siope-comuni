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


