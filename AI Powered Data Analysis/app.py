"""
AI Powered Data Analysis — Gradio chat over a LangGraph data-science agent.

Tools: list/preload CSVs, summaries, safe DataFrame methods, RF classify/regress.
LLM: Groq or Ollama via shared.llm (not OpenAI from the course notebook).
"""

from __future__ import annotations

import os
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

from download_data import main as download_datasets

download_datasets()

from agent import describe_agent, run_query

EXAMPLES = [
    "What CSV files are available?",
    "Summarize both datasets and say which is classification vs regression.",
    "Show the head of classification-dataset.csv",
    "Evaluate the classification dataset — pick a sensible target column.",
    "Evaluate the regression dataset and report R² and MSE.",
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
    return history + [[text, answer]], ""


def build_ui():
    try:
        label = describe_agent()
    except Exception as e:
        label = f"LLM not ready ({e})"

    with gr.Blocks(title="AI Powered Data Analysis") as demo:
        gr.Markdown("# AI Powered Data Analysis")
        gr.Markdown(
            "LangGraph agent: explore course CSVs, inspect columns, "
            "run RandomForest classification / regression.  \n"
            f"**Model:** `{label}`"
        )
        chatbot = gr.Chatbot(height=420, label="Chat")
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask about the datasets…",
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
    demo = build_ui()
    host = os.getenv("GRADIO_HOST", "127.0.0.1")
    port = int(os.getenv("GRADIO_PORT", "7864"))
    demo.launch(server_name=host, server_port=port)
