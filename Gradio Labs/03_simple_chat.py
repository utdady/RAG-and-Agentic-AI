"""03 — Simple Gradio chat over Groq/Ollama (course used Watsonx)."""

from __future__ import annotations

import sys
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.env_load import load_env

load_env(HERE)
from shared.llm import describe_setup, get_llm_info

llm, info = get_llm_info(temperature=0.5)
print(describe_setup())


def generate_response(prompt_txt: str) -> str:
    if not (prompt_txt or "").strip():
        return "Type a question first."
    try:
        out = llm.invoke(prompt_txt)
        return getattr(out, "content", str(out))
    except Exception as e:
        return f"Error: {e}"


chat_application = gr.Interface(
    fn=generate_response,
    allow_flagging="never",
    inputs=gr.Textbox(
        label="Input",
        lines=2,
        placeholder="Type your question here...",
    ),
    outputs=gr.Textbox(label="Output", lines=8),
    title="Simple LLM Chatbot",
    description=(
        f"Ask any question ({info.provider}:{info.model}). "
        "For multi-model comparison see ../Model Comparison Chat/"
    ),
)

if __name__ == "__main__":
    chat_application.launch(server_name="127.0.0.1", server_port=7866, share=False)
