# MCP Labs

Curriculum labs for **MCP**: Context7 clients, multi-server LangGraph hosts,
Calculator MCP, and an **enhanced File Operations** server (progress, elicitation).

Related: [`../Module 4 Integrate Agents, RAG, and Tools with MCP/`](../Module%204%20Integrate%20Agents,%20RAG,%20and%20Tools%20with%20MCP/)

## Prerequisites

- Python 3.11+
- **Node.js / `npx`** for labs `01` and `03`
- Repo-root `.env`: `GROQ_API_KEY` (or Ollama) for agent labs (`03`, `06`, `07`)

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
python 07_file_ops_mcp_client.py
```

Servers:

```powershell
python servers/calculator_server.py --http
python servers/file_ops_server.py
```

File-ops sandbox: `workspace/` (see `sample_hello.py`).

## Scripts

| Script | Topic |
|--------|--------|
| `00`–`02` | Context7 FastMCP clients |
| `03` | LangGraph + Context7 + Met Museum |
| `04`–`06` | Calculator MCP (in-memory / HTTP+stdio / LangGraph) |
| `07_file_ops_mcp_client.py` | Menu client: elicitation, progress, resources, Groq ReAct |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
