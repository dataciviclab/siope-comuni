# Uso operativo del mart labeled

Questa nota spiega come leggere in modo corretto il `mart` finale del progetto:

- dataset: `entrate/comuni_2023_2024`
- tabella: `siope_entrate_comuni_agg_labeled`

## Colonne da usare per prime

- `codice_ente`
- `denominazione_ente`
- `anno`
- `codice_voce`
- `descrizione_codice`
- `importo_totale`
- `importo_totale_eur`
- `is_titolo_9`

## Regole di lettura

- usare `importo_totale_eur` per output leggibili e confronti descrittivi
- usare `importo_totale` solo per controlli tecnici o confronti con i valori raw
- per confronti sui totali tra comuni, partire da `is_titolo_9 = false`
- trattare `is_titolo_9 = true` come flussi tecnici o di giro, non come entrate strutturali

## Join contestuale del dizionario entrate

Il labeled usa un join contestuale tra:

- `codice_comparto` del mart
- `codice_gestione` del dizionario entrate

Nel perimetro v1 dei comuni, il contesto corretto e':

- `tipo_ente = COMUNE`
- `codice_comparto = PRO`

Questa assunzione e' valida per la v1 e va rivalutata se il progetto si estende ad altri comparti.

## Limiti da tenere presenti

- perimetro v1: `comuni / entrate / 2023-2024`
- alcuni path anagrafici sono ancora hardcodati allo snapshot `2024`
- il join anagrafico usa una validita' annuale con pivot al `31 dicembre`
- `codice_col6`, `codice_col7`, `codice_col8` non sono campi interpretativi pubblici

## Query di partenza

Esempio logico per confronti descrittivi:

```sql
select
    denominazione_ente,
    anno,
    sum(importo_totale_eur) as totale_entrate_eur
from read_parquet('out/data/mart/siope_comparto_2y/2024/siope_entrate_comuni_agg_labeled.parquet')
where is_titolo_9 = false
group by 1, 2;
```

La query va adattata al file/anno corretto. Il punto metodologico e' il filtro su `is_titolo_9`.
