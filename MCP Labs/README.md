# MCP Labs

Curriculum labs for **MCP clients** with [FastMCP](https://gofastmcp.com/) talking to
**Context7** (library docs MCP).

Related (build your own server + host):  
[`../Module 4 Integrate Agents, RAG, and Tools with MCP/`](../Module%204%20Integrate%20Agents,%20RAG,%20and%20Tools%20with%20MCP/)

## Prerequisites

- Python 3.11+
- **Node.js / `npx`** for lab `01` (stdio launches `@upstash/context7-mcp`)
- Network access for Context7 (stdio + HTTP)

## Setup

```powershell
cd "MCP Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional: `CONTEXT7_API_KEY` in repo-root `.env` for HTTP lab rate limits.

## Run

```powershell
python 00_stdio_basics.py
python 01_context7_stdio.py
python 02_context7_http.py
```

Lab **01** first run may download the Context7 MCP package via `npx` (can take a minute).

## Scripts

| Script | Topic |
|--------|--------|
| `00_stdio_basics.py` | stdout vs stderr warm-up |
| `01_context7_stdio.py` | `StdioTransport` + `npx @upstash/context7-mcp` |
| `02_context7_http.py` | `StreamableHttpTransport` → `https://mcp.context7.com/mcp` |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
