"""07 — Enhanced file-ops MCP client (elicitation, progress, menu).

Course used Anthropic Claude; here Groq/Ollama via LangGraph ReAct for agent turns,
FastMCP Client for prompts/resources/progress/elicitation.

Usage:
  python 07_file_ops_mcp_client.py
  python 07_file_ops_mcp_client.py servers/file_ops_server.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastmcp import Client
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from shared.llm import describe_setup, get_chat_llm

from _bootstrap import HERE, banner

DEFAULT_SERVER = HERE / "servers" / "file_ops_server.py"


class MCPClient:
    def __init__(self) -> None:
        self.exit_stack = AsyncExitStack()
        self.client: Client | None = None
        self.server_path: str = ""

    async def connect_to_server(self, server_script_path: str) -> None:
        if not (
            server_script_path.endswith(".py")
            or server_script_path.endswith(".js")
            or server_script_path.endswith(".ts")
        ):
            raise ValueError("Server script must be a .py, .js, or .ts file")

        self.server_path = str(Path(server_script_path).resolve())
        self.client = Client(
            self.server_path,
            elicitation_handler=self.handle_elicitation,
            progress_handler=self.handle_progress,
            message_handler=self.handle_message,
        )
        await self.exit_stack.enter_async_context(self.client)

    async def handle_elicitation(
        self, message: str, response_type: type, params, context
    ):
        print(f"Server asks: {message}")
        user_data: dict[str, Any] = {}
        annotations = getattr(response_type, "__annotations__", {}) or {}
        for field_name, field_type in annotations.items():
            type_name = getattr(field_type, "__name__", str(field_type))
            user_input = input(
                f"Enter value for '{field_name}' ({type_name}): "
            ).strip()
            if not user_input:
                try:
                    from fastmcp.client.elicitation import ElicitResult

                    return ElicitResult(action="decline")
                except Exception:
                    return {"action": "decline"}
            user_data[field_name] = user_input
        return response_type(**user_data)

    async def handle_progress(
        self, progress: float, total: float | None, message: str | None
    ) -> None:
        if total is not None and total > 0:
            percentage = (progress / total) * 100
            print(f"Progress: {percentage:.1f}% - {message or ''}")
        else:
            print(f"Progress: {progress} - {message or ''}")

    async def handle_message(self, message) -> None:
        if hasattr(message, "root"):
            method = message.root.method
            print(f"Received: {method}")
            if method == "notifications/tools/list_changed":
                print("Tools have changed — might want to refresh tool cache")
            elif method == "notifications/resources/list_changed":
                print("Resources have changed")

    async def _get_prompts(self):
        assert self.client is not None
        return await self.client.list_prompts()

    async def process_query(self, query: str) -> str:
        """LangGraph ReAct turn with MCP tools (stdio to same server)."""
        mcp = MultiServerMCPClient(
            {
                "file-ops": {
                    "command": sys.executable,
                    "args": [self.server_path],
                    "transport": "stdio",
                    "cwd": str(HERE),
                }
            }
        )
        tools = await mcp.get_tools()
        llm = get_chat_llm(temperature=0.2)
        agent = create_react_agent(model=llm, tools=tools)
        result = await agent.ainvoke({"messages": query})
        last = result["messages"][-1]
        return getattr(last, "content", None) or str(last)

    async def converse(self) -> None:
        print("\nEntering conversation mode. Type 'quit' or 'q' to exit.")
        while True:
            query = input("\nQuery: ").strip()
            if query.lower() in ("quit", "q"):
                break
            if not query:
                print("Please enter a query")
                continue
            try:
                print(await self.process_query(query))
            except Exception as e:
                print(f"Error processing query: {e}")

    async def prompt(self, prompt_name: str) -> None:
        assert self.client is not None
        try:
            prompts_response = await self._get_prompts()
            prompt_obj = next(
                (p for p in prompts_response if p.name == prompt_name), None
            )
            if not prompt_obj:
                print(f"Prompt '{prompt_name}' not found")
                return

            print(prompt_obj)
            arguments: dict[str, str] = {}
            if prompt_obj.arguments:
                for arg in prompt_obj.arguments:
                    required = "required" if arg.required else "optional"
                    user_input = input(f"{arg.name} ({required}): ").strip()
                    if not user_input and arg.required:
                        print(f"Error: {arg.name} is required")
                        return
                    if user_input:
                        arguments[arg.name] = user_input

            prompt_result = await self.client.get_prompt(
                prompt_name, arguments=arguments or None
            )
            prompt_text = prompt_result.messages[0].content.text
            print(await self.process_query(prompt_text))
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}\n")

    async def read_file(self) -> str | None:
        assert self.client is not None
        try:
            file_name = input(
                "Enter file path (relative to workspace/): "
            ).strip()
            encoded = quote(file_name, safe="")
            resource = await self.client.read_resource(f"file:///{encoded}")
            payload = json.loads(resource[0].text)
            if "error" in payload:
                print(payload["error"])
                return None
            content = payload.get("file_content", "")
            print(f"File Content:\n{content}")
            return content
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def _print_dir_listing(self, items: list[dict]) -> None:
        print("\nDirectory Listing:\n")
        print(f"{'Type':<10} {'Size':>10} {'Modified':<25} {'Name'}")
        print("-" * 70)
        for item in items:
            size = f"{item['size']} B"
            print(
                f"{item['type']:<10} {size:>10}  "
                f"{item['modified']:<25} {item['name']}"
            )

    async def read_dir(self) -> None:
        assert self.client is not None
        try:
            resource = await self.client.read_resource("dir://.")
            dir_list = json.loads(resource[0].text)["items"]
            self._print_dir_listing(dir_list)
        except Exception as e:
            print(f"Error reading directory: {e}")

    async def quit_action(self) -> str:
        print("Exiting client...")
        return "quit"

    async def menu(self) -> None:
        print("\nMCP Client Started!")
        print(f"Workspace sandbox: {HERE / 'workspace'}")
        print(describe_setup())

        menu_actions = {
            "1": lambda: self.prompt("documentation_generator"),
            "2": lambda: self.prompt("code_review"),
            "3": self.read_file,
            "4": self.read_dir,
            "5": self.converse,
            "q": self.quit_action,
            "quit": self.quit_action,
        }

        while True:
            choice = input(
                """
Select from the Menu
1. Generate Documentation
2. Review Code
3. Read File
4. Read Current Directory
5. Converse with Agent
q. Quit
> """
            ).strip()
            action = menu_actions.get(choice)
            if not action:
                print("Invalid choice. Please try again.")
                continue
            result = await action()
            if result == "quit":
                break

    async def cleanup(self) -> None:
        if self.exit_stack:
            await self.exit_stack.aclose()


async def main() -> None:
    banner("07 — File Operations MCP client")
    server_path = (
        Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_SERVER
    )
    if not server_path.is_file():
        print(f"Server not found: {server_path}")
        sys.exit(1)

    client = MCPClient()
    try:
        print(f"Connecting to server: {server_path}")
        await client.connect_to_server(str(server_path))
        await client.menu()
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
