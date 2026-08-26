# MCP Servers (FastMCP + Context7) + MCP Application (LangGraph)

## Lab A — FastMCP + Context7 client

Course notebook: Python I/O warm-up, then FastMCP `Client` against Context7 via
stdio (`npx @upstash/context7-mcp`) and HTTP (`https://mcp.context7.com/mcp`).

- `fastmcp` (`Client`, `StdioTransport`, `StreamableHttpTransport`)
- Context7 tools: `resolve-library-id`, `query-docs`

## Lab B — MCP Application (LangGraph multi-server agent)

Course `main.py`:

- `langchain-mcp-adapters.MultiServerMCPClient` — Context7 HTTP + Met Museum stdio
- `langgraph.prebuilt.create_react_agent` + `InMemorySaver`
- OpenAI `ChatOpenAI(model="gpt-5-nano")` (course also listed langchain-ibm; unused)
- CLI menu loop; bug: `if __name__ == "main"` → should be `"__main__"`

## This repo

**Clubbed:** `MCP Labs/` (`00`–`03`).

| Course | Here |
|--------|------|
| FastMCP notebook | `00`–`02` |
| MCP Application `main.py` | `03_langgraph_multiserver_agent.py` |
| OpenAI / Watsonx | Groq/Ollama via `shared.llm.get_chat_llm` |
| `__name__ == "main"` | Fixed |

Cross-link: Module 4 builds a local Connoisseur MCP server + Anthropic host.

