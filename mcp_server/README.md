# MCP Server SIOPE

Tool parlanti per interrogare i dati SIOPE — entrate e uscite degli enti pubblici italiani.

## Tool

| Tool | Cosa fa |
|---|---|
| `siope_cerca_ente` | Cerca enti per nome |
| `siope_get_bilancio` | Totale entrate/uscite annuo di un ente |
| `siope_spesa_categoria` | Composizione per macro-categoria |
| `siope_top_enti` | Classifica enti per importo |
| `siope_serie_storica` | Trend 2021-2025 |
| `siope_enti_comparto` | Elenca enti per comparto/tipo |

## Config MCP

```json
"siope": {
  "command": ["python", "/path/to/open-siope/mcp_server/server.py"],
  "enabled": true
}
```

Dipendenze: `pip install -r mcp_server/requirements.txt`
