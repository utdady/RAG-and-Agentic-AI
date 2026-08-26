"""Gradio AI host — LLM + MCP HTTP tools (Groq / OpenAI-compat).

Usage (server must be running):
  python host_app.py http://127.0.0.1:8000 workspace
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

from client_base import MCPHTTPClient


def _make_llm_client() -> tuple[OpenAI, str]:
    """Groq OpenAI-compatible client when GROQ_API_KEY set; else Ollama / OpenAI."""
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        provider = "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set GROQ_API_KEY in repo-root .env")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        return client, model

    if provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "llama3.2").strip() or "llama3.2"
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        client = OpenAI(api_key=os.getenv("OLLAMA_API_KEY", "ollama"), base_url=base)
        return client, model

    # openai
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY or use LLM_PROVIDER=groq|ollama")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    return OpenAI(api_key=api_key), model


class MCPHTTPHostApp(MCPHTTPClient):
    def __init__(self, server_url: str, roots_dir: str):
        super().__init__(server_url, roots_dir)
        self.conversation_history: list[dict] = []
        self.llm_client, self.model = _make_llm_client()

    async def get_available_tools(self):
        await self.connect()
        mcp_tools = await self.list_tools()
        openai_tools = []

        for tool in mcp_tools:
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or f"Execute {tool.name}",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
            if hasattr(tool, "inputSchema") and tool.inputSchema:
                schema = tool.inputSchema
                if isinstance(schema, dict):
                    if "properties" in schema:
                        tool_schema["function"]["parameters"]["properties"] = schema[
                            "properties"
                        ]
                    if "required" in schema and schema["required"]:
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
                        "description": "List all available resources from the MCP server",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "mcp_read_resource",
                        "description": "Read a specific resource by URI from the MCP server",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "uri": {
                                    "type": "string",
                                    "description": "URI e.g. file://workspace/example.txt",
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
                        "description": "List all available prompt templates from the MCP server",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "mcp_get_prompt",
                        "description": "Get a rendered prompt template from the MCP server",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Prompt template name",
                                },
                                "arguments": {
                                    "type": "object",
                                    "description": "Arguments for the prompt",
                                },
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
            result = "Available resources:\n"
            for resource in resources:
                result += f"- {resource.uriTemplate}"
                if resource.name:
                    result += f" ({resource.name})"
                if resource.description:
                    result += f": {resource.description}"
                result += "\n"
            return result

        if tool_name == "mcp_read_resource":
            uri = arguments.get("uri")
            if not uri:
                return "Error: URI is required"
            try:
                contents = await self.read_resource(uri)
                body = contents.contents if hasattr(contents, "contents") else contents
                if isinstance(body, list) and body:
                    content = body[0]
                    return content.text if hasattr(content, "text") else str(content)
                return str(contents)
            except Exception as e:
                return f"Error reading resource: {e}"

        if tool_name == "mcp_list_prompts":
            prompts = await self.list_prompts()
            result = "Available prompts:\n"
            for prompt in prompts:
                result += f"- {prompt.name}"
                if prompt.description:
                    result += f": {prompt.description}"
                if getattr(prompt, "arguments", None):
                    args = [arg.name for arg in prompt.arguments]
                    result += f" (args: {', '.join(args)})"
                result += "\n"
            return result

        if tool_name == "mcp_get_prompt":
            name = arguments.get("name")
            prompt_args = arguments.get("arguments", {}) or {}
            if not name:
                return "Error: Prompt name is required"
            try:
                messages = await self.get_prompt(name, prompt_args)
                msgs = messages.messages if hasattr(messages, "messages") else messages
                result = f"Prompt: {name}\n\n"
                for msg in msgs:
                    role = getattr(msg, "role", "unknown")
                    content = getattr(msg, "content", "")
                    if hasattr(content, "text"):
                        content = content.text
                    result += f"[{role}]: {content}\n\n"
                return result
            except Exception as e:
                return f"Error getting prompt: {e}"

        try:
            result = await self.call_tool(tool_name, arguments)
            if hasattr(result, "content") and result.content:
                texts = [
                    c.text for c in result.content if hasattr(c, "text") and c.text
                ]
                return "\n".join(texts) if texts else str(result)
            return str(result)
        except Exception as e:
            return f"Error executing tool: {e}"

    async def chat(self, user_message: str, history: list):
        await self.connect()
        self.conversation_history.append({"role": "user", "content": user_message})
        tools = await self.get_available_tools()

        kwargs = {"model": self.model, "messages": self.conversation_history}
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
                tool_result = await self.execute_tool(function_name, function_args)
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
            return []

        with gr.Blocks(title="MCP HTTP AI Host") as interface:
            gr.Markdown(
                f"""
# MCP HTTP AI Host
Chat using MCP HTTP server tools.

**Server:** `{self.server_url}`  
**Workspace Roots:** `{self.roots_dir}`  
**Model:** `{self.model}`
"""
            )
            chatbot = gr.Chatbot(label="Conversation", height=500, type="messages")
            with gr.Row():
                msg = gr.Textbox(
                    label="Your message",
                    placeholder="Ask me to list or read workspace files…",
                    scale=4,
                )
                clear = gr.Button("Clear", scale=1)
            msg.submit(fn=chat_wrapper, inputs=[msg, chatbot], outputs=chatbot).then(
                lambda: "", outputs=msg
            )
            clear.click(fn=reset_conversation, outputs=chatbot)
        return interface


def main() -> None:
    if len(sys.argv) < 3:
        server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")
        roots_dir = str(HERE / "workspace")
        print(f"Using defaults: {server_url} {roots_dir}")
    else:
        server_url = sys.argv[1]
        roots_dir = sys.argv[2]

    client = MCPHTTPHostApp(server_url, roots_dir)
    interface = client.create_interface()
    port = int(os.getenv("GRADIO_HOST_PORT", "7873"))
    interface.queue().launch(server_name="127.0.0.1", server_port=port)


if __name__ == "__main__":
    main()
