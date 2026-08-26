"""01 — Gradio hello world: add two numbers."""

from __future__ import annotations

import gradio as gr


def add_numbers(num1: float, num2: float) -> float:
    return num1 + num2


demo = gr.Interface(
    fn=add_numbers,
    inputs=[gr.Number(label="Num1"), gr.Number(label="Num2")],
    outputs=gr.Number(label="Sum"),
    title="Add Numbers",
    description="Minimal Gradio Interface demo.",
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7864, share=False)
