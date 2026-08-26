# MCP Labs course notes

## Lab A — FastMCP + Context7 client

Python I/O warm-up, then FastMCP `Client` against Context7 (stdio + HTTP).

## Lab B — MCP Application (LangGraph multi-server)

`MultiServerMCPClient` — Context7 HTTP + Met Museum stdio + ReAct agent.
Course bug: `if __name__ == "main"` → `"__main__"`.

## Lab C — MCP Server (Calculator)

FastMCP `CalculatorMCPServer`: `add` / `subtract`, resources, `review_code` prompt.
In-memory `Client(mcp)`, HTTP `run_http_async` on port 8000, stdio subprocess,
LangGraph + `load_mcp_tools` / `MultiServerMCPClient`.

Course wrote `stdio_server.py` with a broken resource f-string
(`return "Document contents of {name"`); fixed in `servers/calculator_server.py`.

## This repo

**Clubbed:** `MCP Labs/` (`00`–`06`).

| Course | Here |
|--------|------|
| Context7 clients | `00`–`02` |
| Multi-server app | `03` |
| Calculator server notebook | `04`–`06` + `servers/calculator_server.py` |
| OpenAI models | Groq/Ollama |
| `path/` wget docs | `data/path/` via `_data.ensure_sample_docs()` |

Cross-link: Module 4 Connoisseur restaurant MCP server.
