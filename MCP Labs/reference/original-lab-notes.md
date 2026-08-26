# MCP Labs course notes

## Lab A — FastMCP + Context7 client

Python I/O warm-up, then FastMCP `Client` against Context7 (stdio + HTTP).

## Lab B — MCP Application (LangGraph multi-server)

`MultiServerMCPClient` — Context7 HTTP + Met Museum stdio + ReAct agent.
Course bug: `if __name__ == "main"` → `"__main__"`.

## Lab C — MCP Server (Calculator)

FastMCP `CalculatorMCPServer`: `add` / `subtract`, resources, prompts.
In-memory / HTTP / stdio clients + LangGraph host.

## Lab D — Enhanced MCP Server (File Operations)

Course repo: `joshuazhou744/enhanced-mcp-server` (branch `start`).

- Server: `write_file` / `delete_file` with `ctx.report_progress`, resources
  `file:///` + `dir://.`, prompts `code_review` + `documentation_generator`
  (elicitation via `DocumentGeneratorSchema`)
- Client: FastMCP handlers (elicitation, progress, messages) + Anthropic Claude
  agentic tool loop + interactive menu

## Lab E — Custom MCP Client (official SDK)

Course “Custom MCP Client”: build `ClientSession` + `stdio_client` by hand against
a simple FastMCP lab server (`echo`, `write_file`, resources, `review_file` prompt).

Course bugs fixed: `def init` → `__init__`, `if __name__ == "main"` → `__main__`.

## This repo

**Clubbed:** `MCP Labs/` (`00`–`08`).

| Course | Here |
|--------|------|
| Context7 clients | `00`–`02` |
| Multi-server app | `03` |
| Calculator server | `04`–`06` + `servers/calculator_server.py` |
| Enhanced file-ops | `servers/file_ops_server.py` + `07` |
| Custom MCP client | `08_custom_mcp_client.py` + `servers/lab_server.py` |
| Claude / OpenAI | Groq/Ollama on agent labs; **08 needs no LLM** |
| `Path.cwd()` / resources | `servers/lab_resources/` |

Cross-link: Module 4 Connoisseur restaurant MCP server.

