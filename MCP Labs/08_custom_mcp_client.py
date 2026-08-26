"""08 — Custom MCP client using the official mcp SDK (ClientSession + stdio).

Course Custom MCP Client lab. Fixes: __init__, __main__, JSON hints.

Usage:
  python 08_custom_mcp_client.py servers/lab_server.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from _bootstrap import HERE, banner

DEFAULT_SERVER = HERE / "servers" / "lab_server.py"


class MCPClient:
    def __init__(self) -> None:
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()

    async def connect(self, server_script: str) -> None:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(Path(server_script).resolve())],
            cwd=str(Path(server_script).resolve().parent),
            env=None,
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()
        print("Connected to MCP server")

    async def list_tools(self):
        assert self.session is not None
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, arguments: dict):
        assert self.session is not None
        return await self.session.call_tool(tool_name, arguments)

    async def list_resources(self):
        assert self.session is not None
        result = await self.session.list_resource_templates()
        return result.resourceTemplates

    async def read_resource(self, uri: str):
        assert self.session is not None
        return await self.session.read_resource(uri)

    async def list_prompts(self):
        assert self.session is not None
        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name: str, arguments: dict):
        assert self.session is not None
        return await self.session.get_prompt(prompt_name, arguments)

    async def run(self) -> None:
        print("\n=== MCP Client ===")
        print(
            "Commands: tools | call | resources | read | prompts | prompt | quit\n"
        )
        while True:
            cmd = input("> ").strip().lower()
            if cmd == "quit":
                break
            try:
                if cmd == "tools":
                    tools = await self.list_tools()
                    for t in tools:
                        print(f"  - {t.name}: {t.description}")

                elif cmd == "call":
                    tool_name = input("  Tool name: ").strip()
                    print(
                        '  Arguments (JSON, e.g. {"text": "hello"}): '
                    )
                    raw = input("  ").strip()
                    args = json.loads(raw)
                    result = await self.call_tool(tool_name, args)
                    for content in result.content:
                        if hasattr(content, "text"):
                            print(f"  Result: {content.text}")

                elif cmd == "resources":
                    resources = await self.list_resources()
                    if resources:
                        for r in resources:
                            name = getattr(
                                r,
                                "name",
                                getattr(r, "description", "Unnamed resource"),
                            )
                            uri_template = getattr(
                                r,
                                "uriTemplate",
                                getattr(r, "uri", "N/A"),
                            )
                            print(f"  - {name}")
                            print(f"    URI template: {uri_template}")
                    else:
                        print("  No resources available")

                elif cmd == "read":
                    uri = input(
                        '  URI (e.g. file://resources/project_info.txt): '
                    ).strip()
                    result = await self.read_resource(uri)
                    for content in result.contents:
                        if hasattr(content, "text"):
                            print(f"\n{content.text}")

                elif cmd == "prompts":
                    prompts = await self.list_prompts()
                    for p in prompts:
                        args_info = ""
                        if p.arguments:
                            arg_names = [arg.name for arg in p.arguments]
                            args_info = f" (args: {', '.join(arg_names)})"
                        print(f"  - {p.name}: {p.description}{args_info}")

                elif cmd == "prompt":
                    prompt_name = input("  Prompt name: ").strip()
                    print(
                        '  Arguments (JSON, e.g. {"filename": "README.md"}): '
                    )
                    raw = input("  ").strip()
                    args = json.loads(raw)
                    result = await self.get_prompt(prompt_name, args)
                    desc = getattr(result, "description", None) or prompt_name
                    print(f"\n--- Prompt: {desc} ---")
                    for msg in result.messages:
                        content = msg.content
                        if hasattr(content, "text"):
                            content_text = content.text
                        elif isinstance(content, dict):
                            content_text = content.get("text", "")
                        else:
                            content_text = str(content)
                        print(f"{msg.role}: {content_text}")

                else:
                    print("  Unknown command")

            except json.JSONDecodeError:
                print("  Error: Invalid JSON format")
                print(
                    '  Hint: Use double quotes, e.g. {"text": "hello"}'
                )
            except Exception as e:
                print(f"  Error: {e}")
                if "not found" in str(e).lower():
                    print("  Hint: Check the resource URI or filename")

    async def cleanup(self) -> None:
        await self.exit_stack.aclose()


async def main() -> None:
    banner("08 — Custom MCP Client (mcp SDK)")
    server = (
        Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_SERVER
    )
    if not server.is_file():
        print(f"Server not found: {server}")
        print("Usage: python 08_custom_mcp_client.py <server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect(str(server))
        await client.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
