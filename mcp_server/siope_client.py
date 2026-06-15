"""Client DuckDB per dati SIOPE su GCS pubblico.

Legge parquet da GCS via DuckDB con gcs_connect (lab_connectors).
I risultati sono cached con TtlCache (TTL 120s).
"""

from __future__ import annotations

from contextlib import closing
from typing import Any

import duckdb
from lab_connectors.duckdb import gcs_connect
from lab_connectors.mcp.cache import TtlCache

CLEAN_BUCKET = "dataciviclab-clean"
ANNI = [2021, 2022, 2023, 2024, 2025]

ENTI_URL = (
    "s3://dataciviclab-clean/siope/siope_anag_enti_seed/2026"
    "/siope_anag_enti_seed_2026_clean.parquet"
)

_cache = TtlCache(ttl_seconds=120)


def _s3_path(lato: str, anno: int) -> str:
    return (
        f"s3://{CLEAN_BUCKET}/siope/siope_{lato}_comuni/{anno}"
        f"/siope_{lato}_comuni_{anno}_clean.parquet"
    )


def _query(sql: str) -> list[tuple]:
    cached = _cache.get(sql)
    if cached is not None:
        return cached

    # Estrai il path S3 dalla SQL per passarlo a gcs_connect
    # Cerchiamo il pattern s3://... dentro la query
    import re

    m = re.search(r"s3://[^\s']+", sql)
    s3_path = m.group(0) if m else ENTI_URL

    with gcs_connect(s3_path) as con:
        result = con.sql(sql).fetchall()
        _cache.set(sql, result)
        return result


def _query_path(sql_template: str, s3_path: str, **kwargs) -> list[tuple]:
    """Build SQL with params, execute via gcs_connect."""
    sql = sql_template.format(**kwargs)
    cached = _cache.get(sql)
    if cached is not None:
        return cached
    with gcs_connect(s3_path) as con:
        result = con.sql(sql).fetchall()
        _cache.set(sql, result)
        return result


# ── Tool implementations ──────────────────────────────────────────────────


def cerca_ente(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Cerca enti per denominazione (LIKE %query%)."""
    safe = query.replace("'", "''")
    rows = _query(
        f"""
        SELECT codice_ente, denominazione_ente, tipo_ente,
               codice_provincia, codice_istat_comune
        FROM read_parquet('{ENTI_URL}')
        WHERE data_fine = '9999-12-31'
          AND denominazione_ente ILIKE '%{safe}%'
        LIMIT {limit}
        """
    )
    cols = ["codice_ente", "denominazione", "tipo_ente", "provincia", "comune_istat"]
    return [dict(zip(cols, r)) for r in rows]


def get_bilancio(
    codice_ente: str, anno: int, lato: str
) -> dict[str, Any]:
    """Totale entrate/uscite per un ente in un anno (da CLEAN)."""
    path = _s3_path(lato, anno)
    row = _query_path(
        """
        SELECT count(*) as righe,
               count(DISTINCT codice_voce) as voci,
               sum(importo_eur) as totale_eur
        FROM read_parquet('{path}')
        WHERE codice_ente = '{ente}'
          AND is_titolo_9 = false
        """,
        path,
        path=path, ente=codice_ente,
    )[0]
    return {
        "codice_ente": codice_ente,
        "anno": anno,
        "lato": lato,
        "righe": row[0],
        "voci": row[1],
        "totale_eur": round(row[2], 2) if row[2] else 0,
    }


def spesa_categoria(
    codice_ente: str, anno: int, lato: str
) -> list[dict[str, Any]]:
    """Breakdown per macro-categoria di un ente (da CLEAN)."""
    path = _s3_path(lato, anno)
    cat_col = "macro_categoria_v2" if lato == "entrate" else "macro_categoria"
    rows = _query_path(
        """
        SELECT {cat} as categoria,
               sum(importo_eur) as totale_eur,
               count(DISTINCT codice_voce) as voci
        FROM read_parquet('{path}')
        WHERE codice_ente = '{ente}'
          AND is_titolo_9 = false
        GROUP BY categoria
        ORDER BY totale_eur DESC
        """,
        path,
        cat=cat_col, path=path, ente=codice_ente,
    )
    return [
        {"categoria": r[0], "totale_eur": round(r[1], 2), "voci": r[2]}
        for r in rows
    ]


def top_enti(
    anno: int, lato: str, comparto: str | None = None, limit: int = 10
) -> list[dict[str, Any]]:
    """Enti con maggiori entrate/uscite (da CLEAN)."""
    path = _s3_path(lato, anno)
    extra = "AND codice_comparto = '{comp}'" if comparto else ""
    rows = _query_path(
        """
        SELECT codice_ente, denominazione_ente,
               sum(importo_eur) as totale_eur,
               codice_comparto
        FROM read_parquet('{path}')
        WHERE is_titolo_9 = false {extra}
        GROUP BY codice_ente, denominazione_ente, codice_comparto
        ORDER BY totale_eur DESC
        LIMIT {lim}
        """,
        path,
        path=path, extra=extra.format(comp=comparto) if comparto else "",
        lim=limit,
    )
    return [
        {
            "codice_ente": r[0],
            "denominazione": r[1],
            "totale_eur": round(r[2], 2),
            "comparto": r[3],
        }
        for r in rows
    ]


def serie_storica(codice_ente: str, lato: str) -> list[dict[str, Any]]:
    """Trend pluriennale per un ente (da CLEAN)."""
    results = []
    for anno in ANNI:
        path = _s3_path(lato, anno)
        try:
            row = _query_path(
                """
                SELECT coalesce(sum(importo_eur), 0) as totale_eur,
                       count(*) as righe
                FROM read_parquet('{path}')
                WHERE codice_ente = '{ente}'
                  AND is_titolo_9 = false
                """,
                path,
                path=path, ente=codice_ente,
            )[0]
            if row[0]:
                results.append({
                    "anno": anno,
                    "totale_eur": round(row[0], 2),
                    "righe": row[1],
                })
        except Exception:
            continue
    return results


def elenca_enti(
    comparto: str | None = None, tipo: str | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """Elenca enti, opzionalmente filtrati per comparto o tipo."""
    conditions = ["data_fine = '9999-12-31'"]
    if comparto:
        conditions.append(f"tipo_ente = '{comparto}'")
    if tipo:
        conditions.append(f"tipo_ente = '{tipo}'")
    where = " AND ".join(conditions)
    rows = _query(
        f"""
        SELECT codice_ente, denominazione_ente, tipo_ente,
               codice_provincia, codice_istat_comune
        FROM read_parquet('{ENTI_URL}')
        WHERE {where}
        ORDER BY denominazione_ente
        LIMIT {limit}
        """
    )
    cols = ["codice_ente", "denominazione", "tipo_ente", "provincia", "comune_istat"]
    return [dict(zip(cols, r)) for r in rows]
