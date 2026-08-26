"""02 — FastMCP Client + Context7 via StreamableHttpTransport."""

from __future__ import annotations

import asyncio
import json
import os

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from _bootstrap import CONTEXT7_HTTP_URL, banner, tool_text


async def run() -> None:
    banner("02 — Context7 MCP (HTTP)")

    url = os.getenv("CONTEXT7_MCP_URL", CONTEXT7_HTTP_URL).strip() or CONTEXT7_HTTP_URL
    headers = {}
    api_key = os.getenv("CONTEXT7_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    kwargs = {"url": url}
    if headers:
        kwargs["headers"] = headers

    transport = StreamableHttpTransport(**kwargs)
    client = Client(transport)

    async with client:
        tools = await client.list_tools()
        print(f"Tools available: {len(tools)}")
        for tool in tools:
            schema = getattr(tool, "inputSchema", None) or getattr(
                tool, "input_schema", None
            )
            print(f"\n{tool.name}:")
            print(f"  {tool.description}")
            if schema is not None:
                print(f"  inputSchema: {json.dumps(schema)[:400]}")

        print("\n=== resolve-library-id (fastmcp) ===")
        response = await client.call_tool(
            "resolve-library-id",
            {
                "libraryName": "fastmcp",
                "query": (
                    "I want to create a new MCP server using the fastmcp "
                    "Python framework"
                ),
            },
        )
        print(tool_text(response, limit=1000))

        print("\n=== query-docs (fastmcp llms.txt) ===")
        docs = await client.call_tool(
            "query-docs",
            {
                "libraryId": "/llmstxt/gofastmcp_llms-full_txt",
                "query": "I want to fetch the code snippets and the documentation",
                "tokens": 5000,
            },
        )
        print(tool_text(docs, limit=500))

    print("\nDone.")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
