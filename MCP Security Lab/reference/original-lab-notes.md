# MCP Security with Permissions and Elicitation

Course: permission-aware FastMCP stdio server + Gradio client/host with allow/ask/deny,
audit log, Approve & Execute, and chat yes/no approval.

## Course stack

- `mcp`, `fastmcp`, `gradio`, `openai` (`gpt-4o-mini`)
- Gradio ports 7863 / 7864

## This repo

**Standalone:** `MCP Security Lab/`

| Course | Here |
|--------|------|
| `mcp_permission_server.py` | `server.py` (+ path sandbox) |
| `mcp_permission_client_base.py` | `client_base.py` |
| `mcp_permission_client_app.py` | `client_app.py` → **7874** |
| `mcp_permission_host_app.py` | `host_app.py` → **7875**, Groq/Ollama |
| `data/` | `test.txt`, `permissions.json` |

`execute_command` remains simulated only.
