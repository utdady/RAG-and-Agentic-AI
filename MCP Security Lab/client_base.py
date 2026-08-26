"""Base MCP client with allow / ask / deny permissions and audit logging."""

from __future__ import annotations

import json
import sys
from contextlib import AsyncExitStack
from datetime import datetime
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
DEFAULT_PERMISSIONS = {
    "read_file": "allow",
    "write_file": "ask",
    "delete_file": "deny",
    "execute_command": "deny",
}


class MCPPermissionClient:
    def __init__(
        self,
        server_script: str,
        permissions_file: str | Path | None = None,
    ):
        self.server_script = str(Path(server_script).resolve())
        self.permissions_file = Path(
            permissions_file or (HERE / "data" / "permissions.json")
        )
        self.permissions_file.parent.mkdir(parents=True, exist_ok=True)
        self.audit_log_file = self.permissions_file.parent / "audit.log"
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._connected = False
        self.permissions = self.load_permissions()

    async def connect(self) -> None:
        if self._connected:
            return
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script],
            cwd=str(Path(self.server_script).parent),
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
        self._connected = True

    def load_permissions(self) -> dict:
        if self.permissions_file.exists():
            return json.loads(self.permissions_file.read_text(encoding="utf-8"))
        perms = dict(DEFAULT_PERMISSIONS)
        self.permissions_file.write_text(
            json.dumps(perms, indent=2), encoding="utf-8"
        )
        return perms

    def save_permissions(self) -> None:
        self.permissions_file.write_text(
            json.dumps(self.permissions, indent=2), encoding="utf-8"
        )

    def check_permission(self, tool_name: str, arguments: dict) -> str:
        arg_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
        if arg_key in self.permissions:
            return self.permissions[arg_key]
        return self.permissions.get(tool_name, "ask")

    def log_audit(self, operation: str, decision: str, reason: str = "") -> None:
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {operation} - Decision: {decision}"
        if reason:
            log_entry += f" - Reason: {reason}"
        log_entry += "\n"
        with open(self.audit_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    async def list_tools(self):
        await self.connect()
        assert self.session is not None
        result = await self.session.list_tools()
        return result.tools

    async def call_tool_with_permission(
        self,
        tool_name: str,
        arguments: dict | None = None,
        approved: bool = False,
    ):
        await self.connect()
        assert self.session is not None
        if arguments is None:
            arguments = {}

        permission = self.check_permission(tool_name, arguments)

        if permission == "deny":
            self.log_audit(f"TOOL: {tool_name}", "DENIED", "Policy: deny")
            return [
                type("obj", (), {"text": f"Permission denied for tool: {tool_name}"})()
            ]

        if permission == "ask" and not approved:
            self.log_audit(f"TOOL: {tool_name}", "ASK", "Awaiting approval")
            approval_msg = (
                f"Permission required for tool: {tool_name}\n"
                f"Arguments: {json.dumps(arguments, indent=2)}\n\n"
                "This tool requires approval before execution.\n"
                "Please approve this operation in the GUI to proceed."
            )
            return [type("obj", (), {"text": approval_msg})()]

        self.log_audit(f"TOOL: {tool_name}", "ALLOWED", f"Policy: {permission}")
        result = await self.session.call_tool(tool_name, arguments=arguments)
        return result.content

    async def list_resources(self):
        await self.connect()
        assert self.session is not None
        result = await self.session.list_resources()
        return result.resources

    async def read_resource(self, uri: str):
        await self.connect()
        assert self.session is not None
        result = await self.session.read_resource(uri=uri)
        return result.contents

    async def list_prompts(self):
        await self.connect()
        assert self.session is not None
        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name: str, arguments: dict | None = None):
        await self.connect()
        assert self.session is not None
        if arguments is None:
            arguments = {}
        result = await self.session.get_prompt(
            name=prompt_name, arguments=arguments
        )
        return result.messages

    async def cleanup(self) -> None:
        await self.exit_stack.aclose()
        self._connected = False
        self.session = None
