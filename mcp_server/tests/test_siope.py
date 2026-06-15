"""Tests per MCP server SIOPE.

Usa DuckDB in-memory con dati finti per mockare gcs_connect.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Aggiunge mcp_server/ al path per import
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ── Fixture dati finti ──────────────────────────────────────────────────────

_ENTI_FAKE = [
    ("800000047", "ROMA CAPITALE", "COMUNE", "058", "091"),
    ("011992501", "COMUNE DI MILANO", "COMUNE", "015", "146"),
    ("006479801", "REGIONE LAZIO", "REGIONE", "058", "091"),
    ("006327004", "ASL ROMA 1", "ASL", "058", "091"),
    ("M00010", "MINISTERO TEST", "MINISTERI", "000", "000"),
]

_BILANCIO_ROMA = [
    # count(*), count(DISTINCT codice_voce), sum(importo_eur)
    (3, 2, 1700000.0),
]

_CATEGORIE_ROMA = [
    # categoria, sum(importo_eur), count(DISTINCT codice_voce)
    ("Imposte proprie", 1500000.0, 1),
    ("Trasferimenti correnti", 200000.0, 1),
]

_TOP_ENTI_PRO = [
    # codice_ente, denominazione_ente, sum(importo_eur), codice_comparto
    ("800000047", "ROMA CAPITALE", 1700000.0, "PRO"),
    ("011992501", "COMUNE DI MILANO", 800000.0, "PRO"),
]

_ENTI_FILTRATI = [
    ("800000047", "ROMA CAPITALE", "COMUNE", "058", "091"),
    ("011992501", "COMUNE DI MILANO", "COMUNE", "015", "146"),
]


def _fake_query(sql: str, *args, **kwargs) -> list[tuple]:
    """Mock per _query: restituisce dati in base al contenuto della SQL."""
    if "ILIKE" in sql and "ROMA" in sql:
        return _ENTI_FAKE
    if "ILIKE" in sql:
        return []
    if "tipo_ente = 'COMUNE'" in sql:
        return _ENTI_FILTRATI
    return []


def _fake_query_path(sql_template: str, s3_path: str = "", **kwargs) -> list[tuple]:
    """Mock per _query_path: restituisce dati in base al contenuto della SQL."""
    sql = sql_template.format(**kwargs) if kwargs else sql_template
    # Bilancio query
    if "count(*)" in sql and "count(DISTINCT codice_voce)" in sql:
        # Se l'ente è M00010 (non presente nei fake data), torna 0
        if "M00010" in sql:
            return [(0, 0, 0)]
        return _BILANCIO_ROMA
    # Categoria query
    if "GROUP BY categoria" in sql:
        return _CATEGORIE_ROMA
    # Top enti query
    if "GROUP BY codice_ente" in sql and "ORDER BY totale_eur DESC" in sql:
        return _TOP_ENTI_PRO
    return []


@pytest.fixture(autouse=True)
def _mock_queries():
    """Applica mock a _query e _query_path in siope_client per ogni test."""
    with patch("siope_client._query", side_effect=_fake_query):
        with patch("siope_client._query_path", side_effect=_fake_query_path):
            yield


# ── Tests ───────────────────────────────────────────────────────────────────


@pytest.mark.pure_unit
class TestClient:
    """Test unitari del client SIOPE con DuckDB mockato."""

    def test_cerca_ente(self):
        """cerca_ente deve trovare enti per match parziale."""
        from siope_client import cerca_ente

        results = cerca_ente("ROMA", limit=5)
        assert len(results) >= 1
        assert results[0]["codice_ente"] == "800000047"
        assert results[0]["denominazione"] == "ROMA CAPITALE"

    def test_cerca_ente_no_match(self):
        """cerca_ente deve restituire lista vuota se nessun match."""
        from siope_client import cerca_ente

        results = cerca_ente("INESISTENTE", limit=5)
        assert results == []

    def test_get_bilancio(self):
        """get_bilancio deve sommare correttamente le entrate."""
        from siope_client import get_bilancio

        b = get_bilancio("800000047", 2024, "entrate")
        assert b["codice_ente"] == "800000047"
        assert b["anno"] == 2024
        assert b["totale_eur"] == 1700000.0  # 1M + 500K + 200K
        assert b["voci"] == 2  # 2 distinct codici_voce

    def test_get_bilancio_no_data(self):
        """get_bilancio deve restituire 0 per ente senza dati."""
        from siope_client import get_bilancio

        b = get_bilancio("M00010", 2024, "entrate")
        assert b["totale_eur"] == 0
        assert b["righe"] == 0

    def test_spesa_categoria(self):
        """spesa_categoria deve raggruppare per macro-categoria."""
        from siope_client import spesa_categoria

        c = spesa_categoria("800000047", 2024, "entrate")
        assert len(c) >= 2  # almeno 2 categorie
        cats = {x["categoria"]: x["totale_eur"] for x in c}
        assert "Imposte proprie" in cats
        assert cats["Imposte proprie"] == 1500000.0  # 1M + 500K

    def test_top_enti(self):
        """top_enti deve ordinare per totale decrescente."""
        from siope_client import top_enti

        t = top_enti(2024, "entrate", "PRO", 3)
        assert len(t) >= 2
        # Roma ha 1.7M, Milano ha 800K
        assert t[0]["codice_ente"] == "800000047"
        assert t[1]["codice_ente"] == "011992501"

    def test_elenca_enti(self):
        """elenca_enti deve filtrare per tipo."""
        from siope_client import elenca_enti

        e = elenca_enti(tipo="COMUNE", limit=10)
        assert len(e) == 2  # Roma + Milano
        assert all(x["tipo_ente"] == "COMUNE" for x in e)


@pytest.mark.contract
class TestServer:
    """Test del server MCP — registrazione tool."""

    def test_all_tools_registered(self):
        """Tutti i 6 tool devono essere registrati."""
        from server import mcp

        tools = asyncio.run(mcp.list_tools())
        names = sorted(t.name for t in tools)
        expected = sorted([
            "siope_cerca_ente",
            "siope_enti_comparto",
            "siope_get_bilancio",
            "siope_serie_storica",
            "siope_spesa_categoria",
            "siope_top_enti",
        ])
        assert names == expected

    def test_server_name(self):
        """Il server deve chiamarsi 'siope'."""
        from server import mcp

        assert mcp.name == "siope"


@pytest.mark.smoke
class TestIntegration:
    """Test di integrazione contro GCS reale (opzionali, con SMOKE_TESTS=1)."""

    def test_cache_hit(self):
        """La cache deve accelerare la seconda chiamata identica."""
        from siope_client import get_bilancio
        import time

        t0 = time.time()
        get_bilancio("800000047", 2024, "entrate")
        first = time.time() - t0

        t0 = time.time()
        get_bilancio("800000047", 2024, "entrate")
        second = time.time() - t0

        assert second < first  # cached should be faster

    def test_cache_different_query(self):
        """Query diverse non devono condividere la cache."""
        from siope_client import get_bilancio, spesa_categoria

        get_bilancio("800000047", 2024, "entrate")
        # Different query, different cache key
        r = spesa_categoria("800000047", 2024, "entrate")
        assert len(r) >= 1
