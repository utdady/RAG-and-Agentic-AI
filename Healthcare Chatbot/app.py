"""
Healthcare Chatbot — Gradio + AutoGen (AG2) multi-agent demos.

Tabs:
  1. Symptom consultation (diagnosis → pharmacy → consultation)
  2. Mental health support (emotion analysis → self-care tips)

Educational only — not medical or mental-health care.
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import gradio as gr

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
warnings.filterwarnings("ignore", category=UserWarning)

from healthcare_crew import run_healthcare_consultation
from llm_config import get_llm_config, resolve_provider
from mental_health_crew import run_mental_health_chat


def _provider_banner() -> str:
    try:
        get_llm_config()
        entry = resolve_provider()
        return f"LLM provider: **{entry}**"
    except Exception as e:
        return f"LLM config error: {e}"


def on_healthcare(symptoms: str) -> str:
    try:
        get_llm_config()
        return run_healthcare_consultation(symptoms)
    except Exception as e:
        return f"Error: {e}"


def on_mental(feelings: str) -> str:
    try:
        get_llm_config()
        return run_mental_health_chat(feelings)
    except Exception as e:
        return f"Error: {e}"


def build_ui():
    with gr.Blocks(title="Healthcare Chatbot (AutoGen)") as demo:
        gr.Markdown("# Multi-Agent Healthcare Chatbot (AutoGen)")
        gr.Markdown(
            "AG2 `GroupChat` demos: **symptom consultation** and **mental health support**.  \n"
            "Needs `GROQ_API_KEY` (or Ollama) in repo-root `.env`.  \n"
            "**Not medical advice / not therapy.** Related curriculum: "
            "[`../AutoGen Labs/`](../AutoGen%20Labs/)."
        )
        gr.Markdown(_provider_banner())

        with gr.Tab("Symptom consultation"):
            gr.Markdown(
                "Patient → diagnosis → pharmacy → consultation (`round_robin`, max 5 rounds)."
            )
            symptoms = gr.Textbox(
                label="Describe your symptoms",
                placeholder="e.g. sore throat and mild fever for two days",
                lines=3,
            )
            go_h = gr.Button("Start consultation", variant="primary")
            out_h = gr.Markdown()
            go_h.click(on_healthcare, inputs=symptoms, outputs=out_h)
            gr.Examples(
                examples=[
                    ["Sore throat and mild fever for two days"],
                    ["Twisted ankle after jogging, swelling and pain"],
                ],
                inputs=symptoms,
            )

        with gr.Tab("Mental health support"):
            gr.Markdown(
                "Emotion analysis → self-care tips (`round_robin`, max 3 rounds). "
                "Not crisis care."
            )
            feelings = gr.Textbox(
                label="How are you feeling?",
                placeholder="e.g. stressed about work and having trouble sleeping",
                lines=3,
            )
            go_m = gr.Button("Start support chat", variant="primary")
            out_m = gr.Markdown()
            go_m.click(on_mental, inputs=feelings, outputs=out_m)
            gr.Examples(
                examples=[
                    ["Stressed about work and having trouble sleeping"],
                    ["A bit lonely and unmotivated this week"],
                ],
                inputs=feelings,
            )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name=os.getenv("GRADIO_HOST", "127.0.0.1"),
        server_port=int(os.getenv("GRADIO_PORT", "7871")),
    )
