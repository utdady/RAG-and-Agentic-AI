"""07 — Speech-to-text only (Whisper + Gradio). No LLM / minutes."""

from __future__ import annotations

import sys
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from transformers import pipeline

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(HERE / ".env")
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "Meeting Assistant" / ".env")

from shared.llm import resolve_whisper_model

whisper_id = resolve_whisper_model()
print(f"Loading Whisper: {whisper_id} (first run may download weights)…")
asr_pipe = pipeline(
    "automatic-speech-recognition",
    model=whisper_id,
    chunk_length_s=30,
)


def transcript_audio(audio_file: str | None) -> str:
    if not audio_file:
        return "Upload an audio file first."
    try:
        return asr_pipe(audio_file, batch_size=8)["text"]
    except Exception as e:
        return f"Error: {e}"


iface = gr.Interface(
    fn=transcript_audio,
    inputs=gr.Audio(sources=["upload", "microphone"], type="filepath", label="Audio"),
    outputs=gr.Textbox(label="Transcript", lines=8),
    title="Audio Transcription App",
    description=(
        f"Upload or record audio → Whisper ({whisper_id}). "
        "For transcript + financial cleanup + meeting minutes, see "
        "../Meeting Assistant/"
    ),
    allow_flagging="never",
)

if __name__ == "__main__":
    iface.launch(server_name="127.0.0.1", server_port=7870, share=False)
