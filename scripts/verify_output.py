#!/usr/bin/env python3
"""
verify_output.py — Certificazione qualità output pipeline SIOPE.

Legge solo da parquet locali (out/data/). Exit code:
  0 = PASS/TUTTO OK
  1 = almeno un check CRITICAL

Usage:
  python3 scripts/verify_output.py              # entrate + uscite, ultimo anno
  python3 scripts/verify_output.py --lato entrate --year 2025
  python3 scripts/verify_output.py --ci         # modalità CI (stampa JSON)
"""

import argparse, json, sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent / "out" / "data"
ANNI = [2025]

LATI_CONFIG = {
    "entrate": {
        "clean": "clean/siope_entrate_comuni/{a}/siope_entrate_comuni_{a}_clean.parquet",
        "class_col": "macro_categoria_v2",
        "class_altro": "Altro",
        "mart": {
            "comuni": "mart/siope_entrate_comuni/{a}/siope_entrate_comuni_agg_labeled.parquet",
            "regioni": "mart/siope_entrate_comuni/{a}/siope_entrate_regioni_agg_labeled.parquet",
            "sanita": "mart/siope_entrate_comuni/{a}/siope_entrate_sanita_agg_labeled.parquet",
            "universita": "mart/siope_entrate_comuni/{a}/siope_entrate_universita_agg_labeled.parquet",
        },
    },
    "uscite": {
        "clean": "clean/siope_uscite_comuni/{a}/siope_uscite_comuni_{a}_clean.parquet",
        "class_col": "macro_categoria",
        "class_altro": "Altre spese",
        "mart": {
            "comuni": "mart/siope_uscite_comuni/{a}/siope_uscite_comuni_agg_labeled.parquet",
            "regioni": "mart/siope_uscite_comuni/{a}/siope_uscite_regioni_agg_labeled.parquet",
            "sanita": "mart/siope_uscite_comuni/{a}/siope_uscite_sanita_agg_labeled.parquet",
            "universita": "mart/siope_uscite_comuni/{a}/siope_uscite_universita_agg_labeled.parquet",
        },
    },
}

SOGLIE = {
    "clean_min_rows": 1_000_000,
    "join_territorio_pct": 95.0,
    "join_codgest_pct": 95.0,
    "mart_min_rows_PRO": 100_000,
    "importi_negativi_max": 100,
}


def resolve(cfg, anno):
    return str(ROOT / cfg.format(a=anno))


def check_clean(con, lato, anno, cfg):
    path = resolve(cfg["clean"], anno)
    if not Path(path).exists():
        return {"check": f"clean_{lato}_{anno}_file", "esito": "CRITICAL", "dettaglio": f"file non trovato: {path}"}

    r = con.execute(f"""
        select count(*), count(distinct codice_ente), count(distinct periodo),
               count(*) filter (where importo < 0),
               count(*) filter (where codice_ente is null)
        from read_parquet('{path}')
    """).fetchone()

    righe, enti, periodi, neg, null_ente = r
    esito = "PASS"
    if righe < SOGLIE["clean_min_rows"]:
        esito = "CRITICAL"
    if neg > SOGLIE["importi_negativi_max"]:
        esito = "CRITICAL"
    if null_ente > 0:
        esito = "CRITICAL"

    return {"check": f"clean_{lato}_{anno}", "esito": esito,
            "dettaglio": {"righe": righe, "enti": enti, "periodi": periodi, "importi_neg": neg, "null_ente": null_ente}}


def check_join(con, lato, anno, cfg):
    path = resolve(cfg["clean"], anno)
    if not Path(path).exists():
        return {"check": f"join_{lato}_{anno}", "esito": "SKIP", "dettaglio": "file non trovato"}

    r = con.execute(f"""
        select
            round(100.0 * count(*) filter (where provincia is not null) / count(*), 2),
            round(100.0 * count(*) filter (where has_codgest_match) / count(*), 2),
            round(100.0 * count(*) filter (where denominazione_ente is not null) / count(*), 2)
        from read_parquet('{path}')
    """).fetchone()

    pct_terr, pct_codg, pct_enti = r
    esito = "PASS"
    if pct_terr < SOGLIE["join_territorio_pct"] or pct_codg < SOGLIE["join_codgest_pct"]:
        esito = "CRITICAL"

    return {"check": f"join_{lato}_{anno}", "esito": esito,
            "dettaglio": {"territorio_pct": pct_terr, "codgest_pct": pct_codg, "enti_pct": pct_enti}}


def check_mart(con, lato, anno, cfg, comparto, slug):
    path = resolve(cfg["mart"][slug], anno)
    if not Path(path).exists():
        return {"check": f"mart_{lato}_{anno}_{comparto}", "esito": "SKIP", "dettaglio": "file non trovato"}

    class_col = cfg["class_col"]
    class_altro = cfg["class_altro"]

    r = con.execute(f"""
        select count(*),
               round(sum(importo_totale_eur), 0),
               count(*) filter (where importo_totale_eur < 0),
               count(*) filter (where {class_col} is null),
               round(100.0 * count(*) filter (where {class_col} = '{class_altro}') / count(*), 2)
        from read_parquet('{path}')
    """).fetchone()

    righe, totale, neg, null_class, altro_pct = r
    min_rows = SOGLIE["mart_min_rows_PRO"] if comparto == "PRO" else 10
    esito = "PASS"
    if righe < min_rows:
        esito = "CRITICAL"
    if null_class > 0:
        esito = "CRITICAL"

    return {"check": f"mart_{lato}_{anno}_{comparto}", "esito": esito,
            "dettaglio": {"righe": righe, "totale_eur": totale, "negativi": neg, "null_class": null_class, "altro_pct": altro_pct}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lato", default="all", choices=["entrate", "uscite", "all"])
    p.add_argument("--year", default="2025")
    p.add_argument("--ci", action="store_true", help="Output JSON per CI")
    args = p.parse_args()

    lati = ["entrate", "uscite"] if args.lato == "all" else [args.lato]
    anno = int(args.year)

    con = duckdb.connect()
    checks = []

    for lato in lati:
        cfg = LATI_CONFIG[lato]
        checks.append(check_clean(con, lato, anno, cfg))
        checks.append(check_join(con, lato, anno, cfg))
        for comparto, slug in [("PRO", "comuni"), ("REG", "regioni"), ("SAN", "sanita"), ("UNI", "universita")]:
            checks.append(check_mart(con, lato, anno, cfg, comparto, slug))

    con.close()

    # Esito
    ok = sum(1 for c in checks if c["esito"] == "PASS")
    warn = sum(1 for c in checks if c["esito"] == "WARN")
    crit = sum(1 for c in checks if c["esito"] == "CRITICAL")
    skip = sum(1 for c in checks if c["esito"] == "SKIP")
    globale = "CRITICAL" if crit > 0 else "WARN" if warn > 0 else "PASS"

    if args.ci:
        print(json.dumps({"esito": globale, "checks": checks}, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"  VERIFICA OUTPUT SIOPE {'CI' if args.ci else ''}")
        print(f"{'='*50}")
        print(f"  Esito: {'✅ PASS' if globale == 'PASS' else '⚠️  WARN' if globale == 'WARN' else '❌ CRITICAL'}")
        print(f"  Checks: {ok} ✅  {warn} ⚠️  {crit} ❌  {skip} ⏭️")
        print(f"{'='*50}\n")
        for c in checks:
            ico = {"PASS": "✅", "WARN": "⚠️", "CRITICAL": "❌", "SKIP": "⏭️"}
            det = c["dettaglio"]
            if isinstance(det, str):
                print(f"  {ico[c['esito']]} {c['check']}: {det}")
            else:
                print(f"  {ico[c['esito']]} {c['check']}: {json.dumps(det)}")

    sys.exit(1 if globale == "CRITICAL" else 0)


if __name__ == "__main__":
    main()
