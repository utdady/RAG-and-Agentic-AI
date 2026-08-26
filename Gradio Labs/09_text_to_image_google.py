"""09 — Text-to-image via Google Gemini (GOOGLE_API_KEY from AI Studio)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.env_load import load_env

load_env(HERE)
# Prefer free-tier-friendly Flash Image; override with GEMINI_IMAGE_MODEL
DEFAULT_MODEL = "gemini-2.5-flash-image"


def generate_image(prompt: str):
    prompt = (prompt or "").strip()
    if not prompt:
        return None, "Enter a prompt first."

    api_key = os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv(
        "GEMINI_API_KEY", ""
    ).strip()
    if not api_key:
        return None, (
            "Set GOOGLE_API_KEY (or GEMINI_API_KEY) in .env — "
            "get a key at https://aistudio.google.com/apikey"
        )

    model_id = os.getenv("GEMINI_IMAGE_MODEL", "").strip() or DEFAULT_MODEL

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None, "Install deps: pip install -r requirements-google.txt"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        notes: list[str] = []
        image_path = None
        for part in response.parts or []:
            if getattr(part, "text", None):
                notes.append(part.text)
            inline = getattr(part, "inline_data", None)
            if inline is not None:
                # Prefer SDK helper when present
                if hasattr(part, "as_image"):
                    pil = part.as_image()
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    tmp.close()
                    pil.save(tmp.name)
                    image_path = tmp.name
                elif getattr(inline, "data", None):
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    tmp.write(inline.data)
                    tmp.close()
                    image_path = tmp.name

        if not image_path:
            reason = " ".join(notes) or "No image in response (check model / quota / safety)."
            return None, f"[{model_id}] {reason}"

        status = f"[{model_id}] OK"
        if notes:
            status += "\n" + "\n".join(notes)
        return image_path, status
    except Exception as e:
        return None, f"[{model_id}] Error: {e}"


demo = gr.Interface(
    fn=generate_image,
    inputs=gr.Textbox(
        label="Prompt",
        lines=3,
        placeholder="a white Siamese cat",
        value="a white Siamese cat",
    ),
    outputs=[
        gr.Image(label="Generated image", type="filepath"),
        gr.Textbox(label="Status", lines=4),
    ],
    title="Text → Image (Google Gemini)",
    description=(
        "Uses Gemini image generation via GOOGLE_API_KEY. "
        f"Default model: {DEFAULT_MODEL} (override with GEMINI_IMAGE_MODEL). "
        "Free-tier limits apply; Imagen models usually need billing."
    ),
    examples=[
        ["a white Siamese cat"],
        ["a watercolor painting of a mountain lake at sunrise"],
        ["a simple cartoon robot waving hello"],
    ],
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7872, share=False)
