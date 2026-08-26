"""Base MCP HTTP client (Streamable HTTP) — no GUI."""

from __future__ import annotations

import logging
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logging.getLogger("mcp").setLevel(logging.WARNING)


class MCPHTTPClient:
    """Pure protocol client for a FastMCP HTTP server."""

    def __init__(self, server_url: str, roots_dir: str):
        self.server_url = server_url.rstrip("/")
        self.roots_dir = roots_dir
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._connected = False

    async def connect(self) -> None:
        if self._connected:
            return
        mcp_url = f"{self.server_url}/mcp"
        read, write, _ = await self.exit_stack.enter_async_context(
            streamablehttp_client(mcp_url)
        )
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()
        self._connected = True

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

    async def cleanup(self) -> None:
        await self.exit_stack.aclose()
        self._connected = False
        self.session = None
