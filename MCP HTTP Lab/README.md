# MCP HTTP Lab

Standalone Gradio apps for **Streamable HTTP MCP**: workspace **roots**, educational
**sampling** stub, protocol client UI, and an AI host that calls MCP tools.

Related curriculum: [`../MCP Labs/`](../MCP%20Labs/)

## Setup

```powershell
cd "MCP HTTP Lab"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env`: `GROQ_API_KEY` (for `host_app.py`).

## Run (3 terminals)

**1 — HTTP MCP server** (port **8000** — stop other MCP HTTP servers first):

```powershell
python server.py
```

**2 — Protocol Gradio client** → http://127.0.0.1:7872

```powershell
python client_app.py http://127.0.0.1:8000 workspace
```

**3 — AI host Gradio chat** → http://127.0.0.1:7873

```powershell
python host_app.py http://127.0.0.1:8000 workspace
```

Defaults work if you omit args (uses `http://127.0.0.1:8000` + local `workspace/`).

## Ports

| App | Port |
|-----|------|
| MCP HTTP server | 8000 |
| Gradio client | **7872** (course 7861) |
| Gradio AI host | **7873** (course 7862; avoids Icebreaker) |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
