"""
Connoisseur Companion — fused Modules 1–4 (California dining AI).

Tabs:
  - Chat: MCP ReAct host (Module 4) with Groq/Ollama
  - Deep recommendations: multi-agent workflow (Module 3) + RAG (Module 2)

Usage:
  python app.py
  Open http://127.0.0.1:7876
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import gradio as gr
from fastmcp.client import Client, PythonStdioTransport
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

os.chdir(HERE)

from shared.env_load import load_env

load_env(HERE)

warnings.filterwarnings("ignore", category=DeprecationWarning)

from agents.workflow import format_recommendations, run_recommendation_workflow
from shared.llm import describe_setup, get_chat_llm

SERVER_SCRIPT = str(HERE / "mcp" / "server.py")
SYSTEM_PROMPT = """You are Connoisseur Companion, an expert AI restaurant guide for California dining.
Use MCP tools for restaurant lookup, vibe search, reviews, and knowledge-base search.
Always call tools when the user asks for specific restaurants, vibes, or recommendations grounded in data.
Be concise and friendly."""

PORT = int(os.getenv("CONNOISSEUR_PORT", "7876"))


async def chat_with_agent(user_message: str, history: list) -> str:
    transport = PythonStdioTransport(script_path=SERVER_SCRIPT)

    async with Client(transport) as client:
        mcp_tools = await client.list_tools()
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema,
                },
            }
            for t in mcp_tools
        ]

        model = get_chat_llm(temperature=0.5).bind_tools(openai_tools)

        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for msg in history or []:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user" and content:
                messages.append(HumanMessage(content=content))
            elif role == "assistant" and content:
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=user_message))

        for _ in range(10):
            response = await model.ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                raw = response.content
                if isinstance(raw, list):
                    return " ".join(
                        b.get("text", "") if isinstance(b, dict) else str(b)
                        for b in raw
                    )
                return str(raw)

            for tool_call in response.tool_calls:
                result = await client.call_tool(tool_call["name"], tool_call["args"])
                tool_output = " ".join(
                    item.text if hasattr(item, "text") else str(item)
                    for item in (result.content or [])
                ) or "(no result)"
                messages.append(
                    ToolMessage(content=tool_output, tool_call_id=tool_call["id"])
                )

    return "I couldn't complete that request. Please try again."


async def handle_chat(user_message, history):
    if history is None:
        history = []
    if not user_message or not str(user_message).strip():
        yield history
        return

    history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": "Thinking..."},
    ]
    yield history

    try:
        response_text = await chat_with_agent(user_message, history[:-2])
    except Exception as e:
        response_text = f"Error: {e}"

    history[-1] = {"role": "assistant", "content": response_text}
    yield history


def handle_deep_recommendations(preferences: str) -> str:
    if not preferences or not preferences.strip():
        return "Describe what you're in the mood for (cuisine, vibe, location, budget)."
    try:
        result = run_recommendation_workflow(preferences.strip())
        return format_recommendations(result)
    except Exception as e:
        return f"Error running recommendation workflow: {e}"


def build_ui():
    with gr.Blocks(title="Connoisseur Companion") as demo:
        gr.Markdown(
            "# Connoisseur Companion\n"
            "Fused IBM course Modules 1–4: structured dining data, multimodal RAG, "
            "multi-agent recommendations, and MCP tools.\n\n"
            f"_{describe_setup()}_"
        )

        with gr.Tab("Chat (MCP + tools)"):
            gr.Markdown(
                "Ask about California restaurants by name, vibe, or review. "
                "The host uses MCP tools backed by Module 1 data and Module 2 retrieval."
            )
            chatbot = gr.Chatbot(height=480, type="messages")
            msg = gr.Textbox(
                label="Message",
                placeholder='e.g. "Find moody steakhouses in DTLA" or "Review for Iron & Embers"',
            )
            with gr.Row():
                b1 = gr.Button("Moody restaurants", size="sm")
                b2 = gr.Button("Iron & Embers", size="sm")
                b3 = gr.Button("Zen sushi in Little Tokyo", size="sm")

            msg.submit(handle_chat, [msg, chatbot], [chatbot])
            msg.submit(lambda: "", None, msg)
            b1.click(
                handle_chat,
                [gr.State("Find me some moody restaurants"), chatbot],
                [chatbot],
            )
            b2.click(
                handle_chat,
                [gr.State("Tell me about Iron & Embers"), chatbot],
                [chatbot],
            )
            b3.click(
                handle_chat,
                [gr.State("What's a zen sushi spot in Little Tokyo?"), chatbot],
                [chatbot],
            )

        with gr.Tab("Deep recommendations"):
            gr.Markdown(
                "Multi-agent workflow (Module 3): profile → RAG retrieval → "
                "parallel trend/style/nutrition analysis → final picks."
            )
            pref = gr.Textbox(
                label="What are you craving?",
                lines=4,
                placeholder=(
                    "I want a romantic Italian dinner in Pasadena under $$$, "
                    "preferably with outdoor seating and lighter pasta options."
                ),
            )
            out = gr.Markdown()
            pref.submit(handle_deep_recommendations, pref, out)
            gr.Button("Get recommendations").click(handle_deep_recommendations, pref, out)

        with gr.Tab("About"):
            gr.Markdown(
                """
**Pipeline**
- **Module 1** — `data/` structured restaurants, reviews, recipes, culinary map
- **Module 2** — Chroma RAG (`python -m rag.index`); keyword fallback if index not built
- **Module 3** — six-agent workflow in `agents/workflow.py`
- **Module 4** — FastMCP server in `mcp/server.py`

**Related labs:** [`MCP Labs/`](../MCP%20Labs/), [`MCP HTTP Lab/`](../MCP%20HTTP%20Lab/)

**Setup:** `GROQ_API_KEY` in repo-root `.env` (or Ollama). Optional: `pip install -r requirements.txt` then `python -m rag.index`.
                """
            )

    return demo


if __name__ == "__main__":
    print(f"Starting Connoisseur Companion on port {PORT}...")
    build_ui().launch(server_name="127.0.0.1", server_port=PORT, theme=gr.themes.Soft())
