"""Gradio permission client — manage policies, approve tools, view audit log.

Usage:
  python client_app.py
  python client_app.py server.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import gradio as gr

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from client_base import MCPPermissionClient

DEFAULT_SERVER = HERE / "server.py"


class MCPPermissionClientApp(MCPPermissionClient):
    def __init__(self, server_script: str):
        super().__init__(server_script)
        self.tools_cache: list[str] = []
        self.prompts_cache: list[str] = []

    async def gui_list_tools(self):
        tools = await self.list_tools()
        output = "Available tools:\n\n"
        self.tools_cache = []
        for tool in tools:
            tool_name = tool.name
            permission = self.permissions.get(tool_name, "ask")
            self.tools_cache.append(tool_name)
            output += f"- {tool_name}\n  Permission: {permission.upper()}\n"
            if tool.description:
                output += f"  Description: {tool.description}\n"
            output += "\n"
        choices = [
            f"{name} ({self.permissions.get(name, 'ask')})"
            for name in self.tools_cache
        ]
        return output, gr.update(choices=choices)

    async def gui_call_tool(
        self, tool_selection: str, arguments_json: str, approved: bool = False
    ):
        if not tool_selection:
            return "Please select a tool first"
        tool_name = tool_selection.split(" (")[0]
        try:
            arguments = (
                json.loads(arguments_json) if arguments_json.strip() else {}
            )
        except json.JSONDecodeError as e:
            return f"Invalid JSON in arguments: {e}"

        result = await self.call_tool_with_permission(
            tool_name, arguments, approved=approved
        )
        if isinstance(result, list) and result:
            content = result[0]
            return content.text if hasattr(content, "text") else str(content)
        return str(result)

    async def gui_list_resources(self):
        resources = await self.list_resources()
        output = "Available resources:\n\n"
        for resource in resources:
            output += f"- {resource.uri}\n"
            if resource.name:
                output += f"  Name: {resource.name}\n"
            if resource.description:
                output += f"  Description: {resource.description}\n"
            output += "\n"
        return output

    async def gui_read_resource(self, uri: str):
        if not uri.strip():
            return "Please enter a resource URI"
        contents = await self.read_resource(uri)
        if isinstance(contents, list) and contents:
            content = contents[0]
            return content.text if hasattr(content, "text") else str(content)
        return str(contents)

    async def gui_list_prompts(self):
        prompts = await self.list_prompts()
        output = "Available prompts:\n\n"
        self.prompts_cache = []
        for prompt in prompts:
            self.prompts_cache.append(prompt.name)
            output += f"- {prompt.name}\n"
            if prompt.description:
                output += f"  Description: {prompt.description}\n"
            if getattr(prompt, "arguments", None):
                args = [arg.name for arg in prompt.arguments]
                output += f"  Arguments: {', '.join(args)}\n"
            output += "\n"
        return output, gr.update(choices=self.prompts_cache)

    async def gui_get_prompt(self, prompt_name: str, arguments_json: str):
        if not prompt_name:
            return "Please select a prompt first"
        try:
            arguments = (
                json.loads(arguments_json) if arguments_json.strip() else {}
            )
        except json.JSONDecodeError as e:
            return f"Invalid JSON in arguments: {e}"
        messages = await self.get_prompt(prompt_name, arguments)
        output = f"Prompt: {prompt_name}\n\n"
        for msg in messages:
            role = getattr(msg, "role", "unknown")
            content = getattr(msg, "content", "")
            if hasattr(content, "text"):
                content = content.text
            output += f"[{role}]: {content}\n\n"
        return output

    async def gui_configure_permission(self, tool_name: str, policy: str):
        if not tool_name:
            return "Please enter a tool name"
        if policy not in {"allow", "deny", "ask"}:
            return "Policy must be: allow, deny, or ask"
        self.permissions[tool_name] = policy
        self.save_permissions()
        return (
            f"Permission updated: {tool_name} = {policy}\n"
            f"Saved to {self.permissions_file}"
        )

    async def gui_view_audit_log(self):
        if not self.audit_log_file.exists():
            return "No audit log entries yet."
        return self.audit_log_file.read_text(encoding="utf-8")

    def create_interface(self):
        with gr.Blocks(title="MCP Permission Client") as interface:
            gr.Markdown(
                "# MCP Permission Client\n"
                "Manage permissions, view audit logs, and call MCP tools securely."
            )
            with gr.Tabs():
                with gr.Tab("Tools"):
                    with gr.Row():
                        with gr.Column():
                            list_tools_btn = gr.Button(
                                "List Tools", variant="primary"
                            )
                            tools_output = gr.Textbox(
                                label="Available Tools", lines=10
                            )
                        with gr.Column():
                            tool_dropdown = gr.Dropdown(
                                label="Select Tool",
                                choices=[],
                                interactive=True,
                            )
                            tool_args = gr.Textbox(
                                label="Arguments (JSON)",
                                placeholder='{"filepath": "test.txt"}',
                                lines=3,
                            )
                            with gr.Row():
                                call_tool_btn = gr.Button(
                                    "Call Tool", variant="primary"
                                )
                                approve_tool_btn = gr.Button(
                                    "Approve & Execute", variant="secondary"
                                )
                            tool_result = gr.Textbox(label="Result", lines=10)

                    list_tools_btn.click(
                        fn=self.gui_list_tools,
                        outputs=[tools_output, tool_dropdown],
                    )
                    call_tool_btn.click(
                        fn=self.gui_call_tool,
                        inputs=[tool_dropdown, tool_args],
                        outputs=tool_result,
                    )

                    async def gui_approve_tool(tool_selection, arguments_json):
                        return await self.gui_call_tool(
                            tool_selection, arguments_json, approved=True
                        )

                    approve_tool_btn.click(
                        fn=gui_approve_tool,
                        inputs=[tool_dropdown, tool_args],
                        outputs=tool_result,
                    )

                with gr.Tab("Resources"):
                    with gr.Row():
                        with gr.Column():
                            list_resources_btn = gr.Button(
                                "List Resources", variant="primary"
                            )
                            resources_output = gr.Textbox(
                                label="Available Resources", lines=10
                            )
                        with gr.Column():
                            resource_uri = gr.Textbox(
                                label="Resource URI",
                                placeholder="file://audit/log",
                            )
                            read_resource_btn = gr.Button(
                                "Read Resource", variant="primary"
                            )
                            resource_content = gr.Textbox(
                                label="Resource Content", lines=10
                            )
                    list_resources_btn.click(
                        fn=self.gui_list_resources, outputs=resources_output
                    )
                    read_resource_btn.click(
                        fn=self.gui_read_resource,
                        inputs=resource_uri,
                        outputs=resource_content,
                    )

                with gr.Tab("Prompts"):
                    with gr.Row():
                        with gr.Column():
                            list_prompts_btn = gr.Button(
                                "List Prompts", variant="primary"
                            )
                            prompts_output = gr.Textbox(
                                label="Available Prompts", lines=5
                            )
                        with gr.Column():
                            prompt_dropdown = gr.Dropdown(
                                label="Select Prompt",
                                choices=[],
                                interactive=True,
                            )
                            prompt_args = gr.Textbox(
                                label="Arguments (JSON)",
                                placeholder=(
                                    '{"operation": "write_file", '
                                    '"risk_level": "MEDIUM"}'
                                ),
                                lines=2,
                            )
                            get_prompt_btn = gr.Button(
                                "Get Prompt", variant="primary"
                            )
                            prompt_result = gr.Textbox(
                                label="Prompt Messages", lines=10
                            )
                    list_prompts_btn.click(
                        fn=self.gui_list_prompts,
                        outputs=[prompts_output, prompt_dropdown],
                    )
                    get_prompt_btn.click(
                        fn=self.gui_get_prompt,
                        inputs=[prompt_dropdown, prompt_args],
                        outputs=prompt_result,
                    )

                with gr.Tab("Permissions"):
                    with gr.Row():
                        with gr.Column():
                            list_tools_for_perm_btn = gr.Button(
                                "Load Tools", size="sm"
                            )
                            perm_tool_name = gr.Dropdown(
                                label="Tool Name",
                                choices=[],
                                allow_custom_value=True,
                            )
                            perm_policy = gr.Radio(
                                choices=["allow", "deny", "ask"],
                                label="Permission Policy",
                                value="ask",
                            )
                            save_perm_btn = gr.Button(
                                "Save Permission", variant="primary"
                            )
                            perm_result = gr.Textbox(label="Result", lines=3)
                        with gr.Column():
                            view_audit_btn = gr.Button(
                                "View Audit Log", variant="secondary"
                            )
                            audit_output = gr.Textbox(
                                label="Audit Log", lines=15
                            )

                    async def load_tools_for_dropdown():
                        tools = await self.list_tools()
                        return gr.update(choices=[t.name for t in tools])

                    list_tools_for_perm_btn.click(
                        fn=load_tools_for_dropdown, outputs=perm_tool_name
                    )
                    save_perm_btn.click(
                        fn=self.gui_configure_permission,
                        inputs=[perm_tool_name, perm_policy],
                        outputs=perm_result,
                    )
                    view_audit_btn.click(
                        fn=self.gui_view_audit_log, outputs=audit_output
                    )

        return interface


def main() -> None:
    server = (
        Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_SERVER
    )
    if not server.is_file():
        print(f"Server not found: {server}")
        sys.exit(1)

    client = MCPPermissionClientApp(str(server))
    interface = client.create_interface()
    port = int(os.getenv("GRADIO_CLIENT_PORT", "7874"))
    interface.queue().launch(server_name="127.0.0.1", server_port=port)


if __name__ == "__main__":
    main()
