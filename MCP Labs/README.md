# MCP Labs

Curriculum labs for **MCP**: FastMCP clients (Context7) and a **LangGraph ReAct**
host over multiple MCP servers (Context7 + Met Museum).

Related (build your own server + host):  
[`../Module 4 Integrate Agents, RAG, and Tools with MCP/`](../Module%204%20Integrate%20Agents,%20RAG,%20and%20Tools%20with%20MCP/)

## Prerequisites

- Python 3.11+
- **Node.js / `npx`** for labs `01` and `03` (Context7 stdio / Met Museum MCP)
- Network access for Context7 HTTP
- Repo-root `.env`: `GROQ_API_KEY` (or Ollama) for lab `03`

## Setup

```powershell
cd "MCP Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional: `CONTEXT7_API_KEY` / `CONTEXT7_MCP_URL` in `.env`.

## Run

```powershell
python 00_stdio_basics.py
python 01_context7_stdio.py
python 02_context7_http.py
python 03_langgraph_multiserver_agent.py
```

Labs **01** / **03** may download npm packages via `npx` on first run.

## Scripts

| Script | Topic |
|--------|--------|
| `00_stdio_basics.py` | stdout vs stderr warm-up |
| `01_context7_stdio.py` | FastMCP `StdioTransport` + Context7 |
| `02_context7_http.py` | FastMCP `StreamableHttpTransport` + Context7 |
| `03_langgraph_multiserver_agent.py` | LangGraph ReAct + Context7 HTTP + Met Museum stdio |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
