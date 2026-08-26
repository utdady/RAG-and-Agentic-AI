# MCP Labs

Curriculum labs for **MCP**: Context7 clients, LangGraph hosts, Calculator MCP,
enhanced File Operations, and a from-scratch mcp SDK client.

Related Gradio HTTP app (streamable HTTP + roots + AI host):  
[`../MCP HTTP Lab/`](../MCP%20HTTP%20Lab/)

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
python 08_custom_mcp_client.py
```

Lab **08** needs no LLM — interactive `tools | call | resources | read | prompts | prompt | quit`.

## Scripts

| Script | Topic |
|--------|--------|
| `00`–`02` | Context7 FastMCP clients |
| `03` | LangGraph + Context7 + Met Museum |
| `04`–`06` | Calculator MCP |
| `07` | File-ops server client (elicitation / progress / ReAct) |
| `08_custom_mcp_client.py` | Official `mcp` SDK `ClientSession` + `lab_server` |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
