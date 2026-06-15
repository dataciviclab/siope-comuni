"""MCP server per interrogare i dati SIOPE in linguaggio naturale.

Tool parlanti: cerca enti, bilanci, categorie di spesa, top enti, serie storiche.
Legge parquet da GCS via DuckDB + lab-connectors.
"""

from __future__ import annotations

from typing import Any

from lab_connectors.mcp import create_mcp_server, guard_timed

from siope_client import (
    cerca_ente,
    elenca_enti,
    get_bilancio,
    serie_storica,
    spesa_categoria,
    top_enti,
)

SERVER = "siope"

mcp = create_mcp_server(
    name=SERVER,
    instructions=(
        "Connettore MCP per i dati SIOPE (entrate e uscite degli enti pubblici italiani). "
        "Permette di: cercare enti per nome, ottenere il bilancio di un ente, "
        "vedere la composizione per categoria, confrontare enti e vedere serie storiche. "
        "I dati coprono 2021-2025 e tutti i comparti (PRO comuni, REG regioni, "
        "SAN sanità, UNI università, e altri)."
    ),
)


@mcp.tool(
    description=(
        "Cerca enti pubblici italiani per nome o parte del nome. "
        "Restituisce codice, denominazione, tipo ente, provincia."
    ),
    structured_output=True,
)
def siope_cerca_ente(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Cerca enti per denominazione (match parziale)."""
    return guard_timed(cerca_ente, "siope_cerca_ente", query, limit, logger_name=SERVER)


@mcp.tool(
    description=(
        "Totale entrate o uscite di un ente in un anno specifico. "
        "lato='entrate' o 'uscite'. I valori sono in euro."
    ),
    structured_output=True,
)
def siope_get_bilancio(codice_ente: str, anno: int, lato: str) -> dict[str, Any]:
    """Quanto ha speso/incassato un ente in un anno."""
    return guard_timed(get_bilancio, "siope_get_bilancio", codice_ente, anno, lato, logger_name=SERVER)


@mcp.tool(
    description=(
        "Composizione delle entrate/uscite di un ente per macro-categoria. "
        "Per entrate: Imposte proprie, Trasferimenti, Fondi perequativi, ecc. "
        "Per uscite: Personale, Acquisto beni, Investimenti, Interessi, ecc."
    ),
    structured_output=True,
)
def siope_spesa_categoria(codice_ente: str, anno: int, lato: str) -> list[dict[str, Any]]:
    """Breakdown per categoria di un ente."""
    return guard_timed(spesa_categoria, "siope_spesa_categoria", codice_ente, anno, lato, logger_name=SERVER)


@mcp.tool(
    description=(
        "Classifica degli enti con maggiori entrate o uscite in un anno. "
        "Opzionalmente filtra per comparto (PRO, REG, SAN, UNI, MON, CDC...). "
        "Utile per rispondere a 'qual è il comune che spende di più?'."
    ),
    structured_output=True,
)
def siope_top_enti(anno: int, lato: str, comparto: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    """Enti con i valori più alti."""
    return guard_timed(top_enti, "siope_top_enti", anno, lato, comparto, limit, logger_name=SERVER)


@mcp.tool(
    description="Serie storica 2021-2025 delle entrate o uscite di un ente. Mostra l'andamento anno per anno.",
    structured_output=True,
)
def siope_serie_storica(codice_ente: str, lato: str) -> list[dict[str, Any]]:
    """Trend pluriennale per un ente."""
    return guard_timed(serie_storica, "siope_serie_storica", codice_ente, lato, logger_name=SERVER)


@mcp.tool(
    description=(
        "Elenca gli enti di un comparto (PRO, REG, SAN, UNI, MON, CDC...) "
        "o di un tipo specifico (COMUNE, ASL, ATENEO, REGIONE...)."
    ),
    structured_output=True,
)
def siope_enti_comparto(comparto: str | None = None, tipo: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """Enti per comparto o tipo."""
    return guard_timed(elenca_enti, "siope_enti_comparto", comparto, tipo, limit, logger_name=SERVER)


if __name__ == "__main__":
    mcp.run()
