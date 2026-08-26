"""
Natural Language SQL Agent — Gradio chat over Chinook via create_sql_agent.

Course used Watsonx + remote MySQL. Here: Groq/Ollama + local SQLite Chinook.
Optional DATABASE_URL for MySQL/Postgres (never commit credentials).
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

from download_data import main as download_chinook

if not os.getenv("DATABASE_URL", "").strip():
    download_chinook()

from agent import describe_setup, run_query

EXAMPLES = [
    "How many Album are there in the database?",
    "How many artists are there?",
    "List the top 5 customers by total invoice amount.",
    "Which genre has the most tracks?",
    "What is the name of the employee who supports the most customers?",
]


def chat(message: str, history: list):
    history = history or []
    text = (message or "").strip()
    if not text:
        return history, ""
    try:
        answer = run_query(text)
    except Exception as e:
        answer = f"Error: {e}"
    return history + [[text, answer]], ""


def build_ui():
    try:
        label = describe_setup()
    except Exception as e:
        label = f"Not ready ({e})"

    with gr.Blocks(title="Natural Language SQL Agent") as demo:
        gr.Markdown("# Natural Language SQL Agent")
        gr.Markdown(
            "Ask questions in English; a LangChain SQL agent queries **Chinook** "
            "(local SQLite by default).  \n"
            f"**Setup:** `{label}`  \n"
            "Optional: set `DATABASE_URL` for MySQL/Postgres instead of SQLite."
        )
        chatbot = gr.Chatbot(height=420, label="Chat")
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask about albums, artists, invoices…",
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
    port = int(os.getenv("GRADIO_PORT", "7866"))
    demo.launch(server_name=host, server_port=port)
