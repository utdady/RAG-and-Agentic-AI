"""08 — Image Q&A (VQA): upload an image + ask a question (Groq vision / Ollama / BLIP fallback)."""

from __future__ import annotations

import base64
import io
import os
import sys
from pathlib import Path

import gradio as gr
import requests
from langchain_core.messages import HumanMessage
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.env_load import load_env

load_env(HERE)
from shared.llm import resolve_provider

DEFAULT_GROQ_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"
SAMPLE_URLS = [
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/5uo16pKhdB1f2Vz7H8Utkg/image-1.png",
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/fsuegY1q_OxKIxNhf6zeYg/image-2.png",
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/KCh_pM9BVWq_ZdzIBIA9Fw/image-3.png",
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/VaaYLw52RaykwrE3jpFv7g/image-4.png",
]


def _pil_to_data_url(image: Image.Image) -> str:
    buf = io.BytesIO()
    rgb = image.convert("RGB")
    rgb.save(buf, format="JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def _load_sample(url: str) -> Image.Image:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


def _vision_llm():
    provider = resolve_provider()
    if provider == "groq":
        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required for Groq vision.")
        model = (
            os.getenv("GROQ_VISION_MODEL", "").strip()
            or DEFAULT_GROQ_VISION
        )
        return ChatGroq(model=model, temperature=0.2, api_key=api_key), f"groq:{model}"

    from langchain_ollama import ChatOllama

    model = os.getenv("OLLAMA_VISION_MODEL", "").strip() or "llava"
    return ChatOllama(model=model, temperature=0.2), f"ollama:{model}"


_blip = None


def _blip_caption(image: Image.Image) -> str:
    global _blip
    from transformers import BlipForConditionalGeneration, BlipProcessor

    if _blip is None:
        print("Loading BLIP fallback…")
        proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        _blip = (proc, model)
    proc, model = _blip
    inputs = proc(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    return proc.decode(out[0], skip_special_tokens=True)


def answer_about_image(image: Image.Image | None, question: str) -> str:
    if image is None:
        return "Upload an image (or load a sample) first."
    q = (question or "").strip() or "Describe the photo"
    prompt = (
        "You are a helpful assistant. Answer the following user query "
        f"in 1 or 2 sentences: {q}"
    )
    try:
        llm, label = _vision_llm()
        msg = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": _pil_to_data_url(image)}},
            ]
        )
        out = llm.invoke([msg])
        text = getattr(out, "content", str(out))
        return f"[{label}]\n{text}"
    except Exception as e:
        # Local caption fallback (not true VQA)
        try:
            cap = _blip_caption(image)
            return (
                f"[blip-fallback] Vision LLM unavailable ({e}). "
                f"Caption only: {cap}"
            )
        except Exception as e2:
            return f"Error: {e}\nBLIP fallback also failed: {e2}"


def load_course_sample(idx: str):
    i = int(idx)
    img = _load_sample(SAMPLE_URLS[i])
    return img


with gr.Blocks(title="Image Q&A") as demo:
    gr.Markdown(
        "# Image Q&A (VQA)\n"
        "Ask questions about an image. Prefers **Groq vision** / **Ollama LLaVA**; "
        "falls back to BLIP caption if needed. "
        "Course sample images available below."
    )
    with gr.Row():
        image = gr.Image(type="pil", label="Image")
        with gr.Column():
            question = gr.Textbox(
                label="Question",
                value="Describe the photo",
                placeholder="How many cars are in this image?",
            )
            sample = gr.Dropdown(
                choices=[str(i) for i in range(4)],
                label="Load course sample (0–3)",
                value=None,
            )
            load_btn = gr.Button("Load sample")
            ask_btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=6)
    load_btn.click(load_course_sample, inputs=sample, outputs=image)
    ask_btn.click(answer_about_image, inputs=[image, question], outputs=answer)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7871, share=False)
