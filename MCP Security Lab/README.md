# MCP Security Lab

Standalone Gradio apps for **MCP permissions** (allow / ask / deny), audit logging,
and educational elicitation / approval flows.

Related: [`../MCP Labs/`](../MCP%20Labs/) · [`../MCP HTTP Lab/`](../MCP%20HTTP%20Lab/)

## Setup

```powershell
cd "MCP Security Lab"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env`: `GROQ_API_KEY` for `host_app.py`.

## Run

Client and host each **spawn** `server.py` via stdio (no separate server terminal).

**Permission Gradio client** → http://127.0.0.1:7874

```powershell
python client_app.py
```

**AI host Gradio chat** → http://127.0.0.1:7875

```powershell
python host_app.py
```

Defaults: `write_file=ask`, `delete_file=deny`, `execute_command=deny` (simulated only).
Use **Approve & Execute** in the client, or reply **yes**/**no** in the host chat.

## Ports

| App | Port |
|-----|------|
| Gradio client | **7874** (course 7863) |
| Gradio AI host | **7875** (course 7864) |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
