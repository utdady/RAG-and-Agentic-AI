"""01 — FastMCP Client + Context7 via StdioTransport (npx @upstash/context7-mcp)."""

from __future__ import annotations

import asyncio
import json

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from _bootstrap import (
    CONTEXT7_STDIO_ARGS,
    CONTEXT7_STDIO_COMMAND,
    banner,
    require_npx,
    tool_text,
)


async def run() -> None:
    require_npx()
    banner("01 — Context7 MCP (stdio / npx)")

    transport = StdioTransport(
        command=CONTEXT7_STDIO_COMMAND,
        args=CONTEXT7_STDIO_ARGS,
    )
    print(f"Transport: {transport}")
    client = Client(transport)

    async with client:
        tools = await client.list_tools()
        print(f"\nTools available: {len(tools)}")
        for i, tool in enumerate(tools[:5]):
            schema = getattr(tool, "inputSchema", None) or getattr(
                tool, "input_schema", None
            )
            print(f"\n--- tool[{i}] ---")
            print(f"name: {tool.name}")
            print(f"description: {tool.description}")
            if schema is not None:
                print(f"inputSchema: {json.dumps(schema, indent=2)[:800]}")

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
        print(tool_text(response, limit=1500))

        print("\n=== resolve-library-id (scikit-learn) ===")
        response = await client.call_tool(
            "resolve-library-id",
            {
                "libraryName": "scikit-learn",
                "query": "I want to use scikit-learn package",
            },
        )
        print(tool_text(response, limit=1500))

        print("\n=== query-docs (scikit-learn) ===")
        docs = await client.call_tool(
            "query-docs",
            {
                "libraryId": "/scikit-learn/scikit-learn",
                "query": "I want to fetch the documentation of the package.",
                "tokens": 5000,
            },
        )
        print(tool_text(docs, limit=1000))

    print("\nDone.")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
