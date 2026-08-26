# MCP Servers (FastMCP + Context7)

Course notebook: Python I/O warm-up, then FastMCP `Client` against Context7 via
stdio (`npx @upstash/context7-mcp`) and HTTP (`https://mcp.context7.com/mcp`).

## Course stack

- `fastmcp` (`Client`, `StdioTransport`, `StreamableHttpTransport`)
- Context7 tools: `resolve-library-id`, `query-docs`
- Digression: `requests` against ibm.com (omitted here — not MCP-specific)

## This repo

**Clubbed:** `MCP Labs/` (curriculum CLI).

Cross-link: Module 4 folder builds a local Connoisseur MCP server + Anthropic host;
these labs consume an external docs MCP.

| Course | Here |
|--------|------|
| Notebook cells | `00`–`02` scripts |
| `input()` / `sys.exit` demo | Skipped in `00` |
| Hardcoded Context7 URL | `CONTEXT7_MCP_URL` / `CONTEXT7_API_KEY` optional |
