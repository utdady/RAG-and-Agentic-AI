# Advanced MCP Applications with Streamable HTTP, Roots, and Sampling

Course lab: FastMCP HTTP file server with workspace roots; mcp SDK Streamable HTTP
client; Gradio protocol UI + OpenAI AI host; educational sampling stub.

## Course stack

- `fastmcp`, `mcp`, `httpx`, `uvicorn`, `gradio`, `openai`
- Server `:8000`; Gradio client `:7861`; host `:7862`
- OpenAI `gpt-4o-mini`

## This repo

**Standalone:** `MCP HTTP Lab/`

| Course | Here |
|--------|------|
| `mcp_http_server.py` | `server.py` |
| `mcp_http_client_base.py` | `client_base.py` |
| `mcp_http_client_app.py` | `client_app.py` → **7872** |
| `mcp_http_host_app.py` | `host_app.py` → **7873**, Groq/Ollama |
| `workspace/` | seeded `test.txt` / `README.md` |

Cross-link: [`../MCP Labs/`](../MCP%20Labs/)
