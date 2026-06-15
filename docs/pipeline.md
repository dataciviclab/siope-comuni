# Pipeline

## Struttura del repository

- `entrate/`: dataset entrate
- `uscite/`: dataset uscite
- `anagrafica/`: seed anagrafiche (enti, codici gestionali, comparti, reg/prov)
- `scripts/`: utility (verify_output.py)
- `.github/workflows/`: CI/CD (check + pipeline dispatch)

## Esecuzione

Eseguire prima i seed anagrafici:

```bash
make seeds
```

Poi i dataset principali:

```bash
python3 -m toolkit.cli.app run all --config entrate/dataset.yml
python3 -m toolkit.cli.app run all --config uscite/dataset.yml
```

Il workflow CI su GitHub Actions fa tutto automaticamente via dispatch.

## Output — Entrate

| Layer | Descrizione |
|---|---|
| `clean` | 19 colonne: dati mensili + territorio, comparto, classificazione |
| `siope_entrate_comuni_agg_labeled` | aggregato voci + territorio (provincia + regione) |
| `siope_entrate_regioni_agg_labeled` | regioni e province autonome |
| `siope_entrate_sanita_agg_labeled` | ASL, AO, IRCCS |
| `siope_entrate_universita_agg_labeled` | atenei e dipartimenti |
| `h_entrate_comune_macro` | gerarchia: comune × macro_categoria |
| `h_entrate_provincia_macro` | gerarchia: provincia × macro_categoria |
| `h_entrate_regione_macro` | gerarchia: regione × macro_categoria |

## Output — Uscite

| Layer | Descrizione |
|---|---|
| `clean` | 20 colonne: dati mensili + territorio, comparto, classificazione |
| `siope_uscite_comuni_agg_labeled` | aggregato voci + territorio |
| `siope_uscite_regioni_agg_labeled` | regioni e province autonome |
| `siope_uscite_sanita_agg_labeled` | ASL, AO, IRCCS |
| `siope_uscite_universita_agg_labeled` | atenei e dipartimenti |
| `h_uscite_comune` | gerarchia: comune × macro_categoria |
| `h_uscite_provincia` | gerarchia: provincia × macro_area |
| `h_uscite_regione` | gerarchia: regione × macro_area |

## Output — Cross-comparto

| Layer | Descrizione |
|---|---|
| `siope_bilancio_unificato` | bilancio consolidato su tutti i comparti |

## Limiti noti

- i mart detail mensili non sono generati di default (artifact CI più compatto)
- per confronti descrittivi sui totali, usare come base `is_titolo_9 = false`
- gli importi originari sono in centesimi di euro
- i dati SIOPE sono aggiornati a cadenza mensile dalla fonte; il progetto va rieseguito periodicamente
