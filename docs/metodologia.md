# Metodologia

## Origine dati

Il progetto usa i download open di SIOPE:

- `SIOPE_ENTRATE.{year}.zip` per il dataset principale
- `SIOPE_ANAGRAFICHE.zip` per i seed di supporto

## Pipeline

La pipeline segue il contract del `toolkit`:

- `raw`: download e extraction degli archivi ZIP
- `clean`: normalizzazione minima dei CSV SIOPE
- `mart`: join anagrafici, filtro comuni, aggregazione e labeling

## Regole metodologiche iniziali

- il focus v1 e' solo su `comuni / entrate / 2023-2024`
- il terzo campo delle entrate viene trattato come `periodo` (`01..12`), non come `codice_gestione`
- il join contestuale del labeled usa `codice_comparto = codice_gestione` sul perimetro comuni
- i confronti descrittivi sui totali devono partire da `is_titolo_9 = false`

## Unita' di misura

- `importo`: centesimi di euro
- `importo_totale_eur`: euro derivati dal totale aggregato

## Output v1

Il dataset principale espone:

- `clean` entrate
- `mart` comuni di dettaglio
- `mart` comuni aggregato per `ente-anno-codice_voce`
- `mart` comuni aggregato labeled con descrizioni voce

## Classificazione minima per letture pubbliche

Nel `mart` labeled esiste anche una `macro_categoria_v2` pensata per evitare due
ambiguita' emerse nei follow-up pubblici:

- non confondere i `Fondi perequativi` con le `Imposte proprie`
- non leggere i `Contributi agli investimenti` come se fossero semplici
  `Trasferimenti correnti`

La proxy v1 usa regole volutamente semplici sui codici voce:

- `1.01.*` -> `Imposte proprie`
- `1.03.01.01.001` -> `Fondi perequativi`
- `2.01.*` -> `Trasferimenti correnti`
- `4.02.*` -> `Contributi agli investimenti`
- tutto il resto -> `Altro`

Questa classificazione non sostituisce la lettura puntuale delle singole
`descrizione_codice`, ma rende piu' stabili confronti pubblici come autonomia
fiscale vs dipendenza esterna nei follow-up `D2`, `D3` e `D4`.
