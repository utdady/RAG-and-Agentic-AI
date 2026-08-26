# MCP Labs

Curriculum labs for **MCP**: FastMCP clients, multi-server LangGraph hosts, and a
**Calculator MCP server** (tools / resources / prompts) over in-memory, HTTP, and stdio.

Related (restaurant Connoisseur server):  
[`../Module 4 Integrate Agents, RAG, and Tools with MCP/`](../Module%204%20Integrate%20Agents,%20RAG,%20and%20Tools%20with%20MCP/)

## Prerequisites

- Python 3.11+
- **Node.js / `npx`** for labs `01` and `03`
- Network for Context7 + sample doc download
- Repo-root `.env`: `GROQ_API_KEY` (or Ollama) for labs `03` and `06`

## Setup

```powershell
cd "MCP Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python 00_stdio_basics.py
python 01_context7_stdio.py
python 02_context7_http.py
python 03_langgraph_multiserver_agent.py
python 04_calculator_inmemory.py
python 05_calculator_http_stdio_clients.py
python 06_calculator_langgraph_agent.py
```

Standalone calculator server:

```powershell
python servers/calculator_server.py          # stdio
python servers/calculator_server.py --http   # http://127.0.0.1:8000/mcp
```

## Scripts

| Script | Topic |
|--------|--------|
| `00`–`02` | Context7 FastMCP clients |
| `03` | LangGraph + Context7 + Met Museum |
| `04_calculator_inmemory.py` | Build server + in-memory `Client(mcp)` |
| `05_calculator_http_stdio_clients.py` | HTTP + Stdio transports |
| `06_calculator_langgraph_agent.py` | ReAct over stdio + HTTP calculator |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
