"""
Data Viz Agent — Gradio UI over LangChain pandas dataframe agent.

LLM writes pandas/matplotlib code (allow_dangerous_code). Local/demo use only.
Watsonx → Groq/Ollama via shared.llm.
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

from download_data import main as download_csv

download_csv()

from agent import describe_agent, load_dataframe, run_query

EXAMPLES = [
    "how many rows of data are in this file?",
    "Give me all the data where student's age is over 18 years old.",
    "Generate a bar chart to plot the gender count.",
    "Generate a pie chart to display average value of Walc for each Gender.",
    "Create box plots to analyze the relationship between 'freetime' and 'G3'.",
    "Generate scatter plots for Dalc vs G3 and Walc vs G3.",
    "Use bar plots to compare average G3 for internet yes vs no.",
    "Plot absences vs G3 as a scatter plot.",
]


def chat(message: str, history: list, gallery: list | None):
    history = history or []
    text = (message or "").strip()
    if not text:
        return history, "", gallery or []

    try:
        answer, images = run_query(text)
    except Exception as e:
        answer, images = f"Error: {e}", []

    history = history + [[text, answer]]
    # Gradio Gallery accepts list of images / paths
    return history, "", images or gallery or []


def build_ui():
    try:
        label = describe_agent()
        cols = ", ".join(load_dataframe().columns.astype(str).tolist()[:12])
        col_note = f"Columns (sample): `{cols}…`"
    except Exception as e:
        label = f"Not ready ({e})"
        col_note = ""

    with gr.Blocks(title="Data Viz Agent") as demo:
        gr.Markdown("# Data Viz Agent")
        gr.Markdown(
            "Ask questions or request charts on **student-mat** via a pandas "
            "dataframe agent (`allow_dangerous_code`).  \n"
            f"**Model:** `{label}`  \n{col_note}  \n"
            "⚠️ Local/demo only — the model can execute Python on your machine."
        )
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=420, label="Chat")
                msg = gr.Textbox(
                    placeholder="Ask for stats or a chart…",
                    show_label=False,
                )
                with gr.Row():
                    send = gr.Button("Send", variant="primary")
                    clear = gr.Button("Clear")
            with gr.Column(scale=2):
                gallery = gr.Gallery(
                    label="Latest plots",
                    columns=1,
                    height=420,
                    object_fit="contain",
                )

        gr.Examples(examples=EXAMPLES, inputs=msg)

        send.click(
            chat, inputs=[msg, chatbot, gallery], outputs=[chatbot, msg, gallery]
        )
        msg.submit(
            chat, inputs=[msg, chatbot, gallery], outputs=[chatbot, msg, gallery]
        )
        clear.click(lambda: ([], "", []), outputs=[chatbot, msg, gallery])

    return demo


if __name__ == "__main__":
    demo = build_ui()
    host = os.getenv("GRADIO_HOST", "127.0.0.1")
    port = int(os.getenv("GRADIO_PORT", "7865"))
    demo.launch(server_name=host, server_port=port)
