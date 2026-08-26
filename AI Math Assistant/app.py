"""
AI Math Assistant — Gradio chat over a LangGraph ReAct agent.

Tools: add / subtract / multiply / divide / power + Wikipedia lookup.
LLM: Groq or Ollama via shared.llm (not Watsonx / OpenAI from the course notebook).
"""

from __future__ import annotations

import sys
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shared.env_load import load_env

load_env(HERE)

from agent import describe_agent, run_query


EXAMPLES = [
    "What is 25 divided by 4?",
    "Subtract 100, 20, and 10.",
    "Multiply 2, 3, and 4.",
    "Calculate 5 to the power of 2.",
    "What is the population of Canada? Multiply it by 0.75",
]


def chat(message: str, history: list):
    history = history or []
    text = (message or "").strip()
    if not text:
        return history, ""

    try:
        answer, _ = run_query(text)
    except Exception as e:
        answer = f"Error: {e}"

    history = history + [[text, answer]]
    return history, ""


def build_ui():
    try:
        label = describe_agent()
    except Exception as e:
        label = f"LLM not ready ({e})"

    with gr.Blocks(title="AI Math Assistant") as demo:
        gr.Markdown("# AI Math Assistant")
        gr.Markdown(
            f"LangGraph ReAct agent with arithmetic tools + Wikipedia.  \n"
            f"**Model:** `{label}`"
        )
        chatbot = gr.Chatbot(height=420, label="Chat")
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask a math question or a fact + calculation…",
                scale=4,
                show_label=False,
            )
            send = gr.Button("Send", variant="primary", scale=1)
        gr.Examples(examples=EXAMPLES, inputs=msg)
        clear = gr.Button("Clear")

        send.click(chat, inputs=[msg, chatbot], outputs=[chatbot, msg])
        msg.submit(chat, inputs=[msg, chatbot], outputs=[chatbot, msg])
        clear.click(lambda: ([], ""), outputs=[chatbot, msg])

    return demo


if __name__ == "__main__":
    import os

    demo = build_ui()
    host = os.getenv("GRADIO_HOST", "127.0.0.1")
    port = int(os.getenv("GRADIO_PORT", "7863"))
    demo.launch(server_name=host, server_port=port)
