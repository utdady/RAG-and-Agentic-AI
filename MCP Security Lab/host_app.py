"""Gradio AI host with permission-aware MCP tools (Groq / OpenAI-compat).

Usage:
  python host_app.py
  python host_app.py server.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import gradio as gr
from openai import OpenAI

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shared.env_load import load_env

load_env(HERE)

from client_base import MCPPermissionClient

DEFAULT_SERVER = HERE / "server.py"


def _make_llm_client() -> tuple[OpenAI, str]:
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        provider = "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set GROQ_API_KEY in repo-root .env")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        return (
            OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1"),
            model,
        )

    if provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "llama3.2").strip() or "llama3.2"
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        return (
            OpenAI(
                api_key=os.getenv("OLLAMA_API_KEY", "ollama"), base_url=base
            ),
            model,
        )

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY or use LLM_PROVIDER=groq|ollama")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    return OpenAI(api_key=api_key), model


class MCPPermissionHostApp(MCPPermissionClient):
    def __init__(self, server_script: str):
        super().__init__(server_script)
        self.llm_client, self.model = _make_llm_client()
        self.conversation_history: list[dict] = []
        self.pending_approval: dict | None = None
        self.risk_levels = {
            "read_file": "low",
            "write_file": "medium",
            "delete_file": "high",
            "execute_command": "critical",
        }

    async def get_available_tools(self):
        await self.connect()
        mcp_tools = await self.list_tools()
        openai_tools = []

        for tool in mcp_tools:
            permission = self.permissions.get(tool.name, "ask")
            risk = self.risk_levels.get(tool.name, "medium")
            desc = (tool.description or f"Execute {tool.name}") + (
                f" (Permission: {permission}, Risk: {risk})"
            )
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": desc,
                    "parameters": {"type": "object", "properties": {}},
                },
            }
            if getattr(tool, "inputSchema", None) and isinstance(
                tool.inputSchema, dict
            ):
                schema = tool.inputSchema
                if "properties" in schema:
                    tool_schema["function"]["parameters"]["properties"] = schema[
                        "properties"
                    ]
                if schema.get("required"):
                    tool_schema["function"]["parameters"]["required"] = schema[
                        "required"
                    ]
            openai_tools.append(tool_schema)

        openai_tools.extend(
            [
                {
                    "type": "function",
                    "function": {
                        "name": "mcp_list_resources",
                        "description": "List MCP resources",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "mcp_read_resource",
                        "description": "Read MCP resource by URI",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "uri": {
                                    "type": "string",
                                    "description": "e.g. file://audit/log",
                                }
                            },
                            "required": ["uri"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "mcp_list_prompts",
                        "description": "List MCP prompts",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "mcp_get_prompt",
                        "description": "Get rendered MCP prompt",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "arguments": {"type": "object"},
                            },
                            "required": ["name"],
                        },
                    },
                },
            ]
        )
        return openai_tools

    async def execute_tool(self, tool_name: str, arguments: dict):
        await self.connect()

        if tool_name == "mcp_list_resources":
            resources = await self.list_resources()
            lines = ["Available resources:"]
            for r in resources:
                line = f"- {r.uri}"
                if r.name:
                    line += f" ({r.name})"
                lines.append(line)
            return "\n".join(lines)

        if tool_name == "mcp_read_resource":
            uri = arguments.get("uri")
            if not uri:
                return "Error: URI is required"
            try:
                contents = await self.read_resource(uri)
                if isinstance(contents, list) and contents:
                    c = contents[0]
                    return c.text if hasattr(c, "text") else str(c)
                return str(contents)
            except Exception as e:
                return f"Error reading resource: {e}"

        if tool_name == "mcp_list_prompts":
            prompts = await self.list_prompts()
            lines = ["Available prompts:"]
            for p in prompts:
                line = f"- {p.name}"
                if p.description:
                    line += f": {p.description}"
                lines.append(line)
            return "\n".join(lines)

        if tool_name == "mcp_get_prompt":
            name = arguments.get("name")
            prompt_args = arguments.get("arguments", {}) or {}
            if not name:
                return "Error: Prompt name is required"
            try:
                messages = await self.get_prompt(name, prompt_args)
                result = f"Prompt: {name}\n\n"
                for msg in messages:
                    role = getattr(msg, "role", "unknown")
                    content = getattr(msg, "content", "")
                    if hasattr(content, "text"):
                        content = content.text
                    result += f"[{role}]: {content}\n\n"
                return result
            except Exception as e:
                return f"Error getting prompt: {e}"

        try:
            result = await self.call_tool_with_permission(tool_name, arguments)
            if isinstance(result, list) and result:
                content = result[0]
                text = content.text if hasattr(content, "text") else str(content)
                if (
                    "Permission required for tool:" in text
                    and "Please approve this operation" in text
                ):
                    self.pending_approval = {
                        "tool_name": tool_name,
                        "arguments": arguments,
                    }
                return text
            return str(result)
        except Exception as e:
            return f"Error executing tool: {e}"

    def assess_risk(self, tool_name: str, arguments: dict) -> dict:
        risk_level = self.risk_levels.get(tool_name, "medium")
        permission = self.permissions.get(tool_name, "ask")
        descriptions = {
            "low": "Safe operation with minimal impact",
            "medium": "Moderate impact - modifies data",
            "high": "High impact - destructive operation",
            "critical": "Critical impact - system-level operation",
        }
        return {
            "tool": tool_name,
            "risk_level": risk_level,
            "permission": permission,
            "requires_approval": permission in {"ask", "deny"},
            "description": descriptions.get(risk_level, ""),
        }

    async def chat(self, user_message: str, history: list):
        await self.connect()
        low = user_message.strip().lower()

        if self.pending_approval and low in {
            "yes",
            "approve",
            "ok",
            "confirm",
            "y",
        }:
            tool_name = self.pending_approval["tool_name"]
            arguments = self.pending_approval["arguments"]
            self.pending_approval = None
            result = await self.call_tool_with_permission(
                tool_name, arguments, approved=True
            )
            if isinstance(result, list) and result:
                content = result[0]
                body = content.text if hasattr(content, "text") else str(content)
            else:
                body = str(result)
            response_text = f"Operation approved and executed.\n\n{body}"
            self.conversation_history.append(
                {"role": "user", "content": user_message}
            )
            self.conversation_history.append(
                {"role": "assistant", "content": response_text}
            )
            return response_text

        if self.pending_approval and low in {"no", "deny", "cancel", "n"}:
            self.pending_approval = None
            response_text = "Operation cancelled by user."
            self.conversation_history.append(
                {"role": "user", "content": user_message}
            )
            self.conversation_history.append(
                {"role": "assistant", "content": response_text}
            )
            return response_text

        self.conversation_history.append(
            {"role": "user", "content": user_message}
        )
        tools = await self.get_available_tools()
        kwargs: dict = {
            "model": self.model,
            "messages": self.conversation_history,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.llm_client.chat.completions.create(**kwargs)
        if not response or not response.choices:
            return "Error: No response from LLM"

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in assistant_message.tool_calls
                    ],
                }
            )
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                _ = self.assess_risk(function_name, function_args)
                tool_result = await self.execute_tool(
                    function_name, function_args
                )
                self.conversation_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    }
                )

            final_response = self.llm_client.chat.completions.create(
                model=self.model, messages=self.conversation_history
            )
            if not final_response or not final_response.choices:
                return "Error: No response from LLM after tool execution"
            final_message = final_response.choices[0].message.content
            self.conversation_history.append(
                {"role": "assistant", "content": final_message}
            )
            return final_message

        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message.content}
        )
        return assistant_message.content

    def _get_permission_summary(self) -> str:
        summary = "### Current Permission Policies:\n\n"
        for tool, policy in self.permissions.items():
            risk = self.risk_levels.get(tool, "medium")
            summary += f"- **{tool}**: {policy.upper()} (Risk: {risk})\n"
        return summary

    def create_interface(self):
        async def chat_wrapper(message, history):
            if not message.strip():
                return history
            response = await self.chat(message, history)
            return history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response},
            ]

        async def reset_conversation():
            self.conversation_history = []
            self.pending_approval = None
            return []

        with gr.Blocks(title="MCP Permission AI Host") as interface:
            gr.Markdown(
                f"""
# MCP Permission AI Host
Permission-aware chat with MCP tools.

**Model:** `{self.model}`  
Reply **yes** / **no** when a tool is awaiting approval.
"""
            )
            chatbot = gr.Chatbot(
                label="Conversation", height=500, type="messages"
            )
            with gr.Row():
                msg = gr.Textbox(
                    label="Your message",
                    placeholder="Ask me to read/write files…",
                    scale=4,
                )
                clear = gr.Button("Clear", scale=1)
            with gr.Accordion("Permission Status", open=False):
                gr.Markdown(self._get_permission_summary())
            msg.submit(
                fn=chat_wrapper, inputs=[msg, chatbot], outputs=chatbot
            ).then(lambda: "", outputs=msg)
            clear.click(fn=reset_conversation, outputs=chatbot)
        return interface


def main() -> None:
    server = (
        Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_SERVER
    )
    if not server.is_file():
        print(f"Server not found: {server}")
        sys.exit(1)

    client = MCPPermissionHostApp(str(server))
    interface = client.create_interface()
    port = int(os.getenv("GRADIO_HOST_PORT", "7875"))
    interface.queue().launch(server_name="127.0.0.1", server_port=port)


if __name__ == "__main__":
    main()
