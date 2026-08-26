"""
Style Finder — Gradio fashion catalog matcher + vision LLM analysis.

Upload an outfit image → ResNet50 embedding → cosine match in course pickle →
Groq/Ollama vision write-up with catalog item details.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import gradio as gr
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shared.env_load import load_env

load_env(HERE)

import config
from download_data import main as download_embeddings
from helpers import catalog_table_markdown, get_all_items_for_image, process_response
from image_processor import ImageProcessor
from llm_service import VisionFashionService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

print("Ensuring embeddings dataset…")
download_embeddings()
print(f"Loading dataset from {config.EMBEDDINGS_PATH.name}…")
DATASET = pd.read_pickle(config.EMBEDDINGS_PATH)
logger.info("Dataset rows=%s columns=%s", len(DATASET), list(DATASET.columns))

print("Loading ResNet50…")
PROCESSOR = ImageProcessor(
    image_size=config.IMAGE_SIZE,
    norm_mean=config.NORMALIZATION_MEAN,
    norm_std=config.NORMALIZATION_STD,
)

VISION = None


def _vision() -> VisionFashionService:
    global VISION
    if VISION is None:
        VISION = VisionFashionService()
        print(f"Vision LLM: {VISION.label}")
    return VISION


def analyze_style(image):
    if image is None:
        return None, "Upload an outfit photo first.", "", ""

    encoded = PROCESSOR.encode_image(image, is_url=False)
    if encoded["vector"] is None:
        return None, "Could not encode the image.", "", ""

    match_row, score = PROCESSOR.find_closest_match(encoded["vector"], DATASET)
    if match_row is None:
        return None, "No match found in the catalog.", "", ""

    image_url = match_row.get("Image URL", "")
    related = get_all_items_for_image(image_url, DATASET)
    if related is None or len(related) == 0:
        related = match_row.to_frame().T

    threshold = config.SIMILARITY_THRESHOLD
    kind = "exact-ish match" if score >= threshold else "similar (below threshold)"
    meta = (
        f"**Similarity:** {score:.3f} ({kind}, threshold={threshold})\n\n"
        f"**Matched image URL:** {image_url}\n\n"
        f"{catalog_table_markdown(related)}"
    )

    try:
        raw = _vision().generate_fashion_response(
            encoded["base64"],
            match_row,
            related,
            similarity_score=score,
            threshold=threshold,
        )
        analysis = process_response(raw)
        analysis = f"_Model: {_vision().label}_\n\n{analysis}"
    except Exception as e:
        analysis = (
            f"# Fashion Analysis\n\n"
            f"Vision LLM unavailable ({e}). Catalog match is shown below.\n\n"
            f"{catalog_table_markdown(related)}"
        )

    # Show matched catalog image if URL is fetchable; else user image
    matched_preview = image
    try:
        if isinstance(image_url, str) and image_url.startswith("http"):
            enc = PROCESSOR.encode_image(image_url, is_url=True)
            if enc.get("pil") is not None:
                matched_preview = enc["pil"]
    except Exception:
        pass

    status = f"Score={score:.3f} | items={len(related)} | {kind}"
    return matched_preview, analysis, meta, status


with gr.Blocks(title="Style Finder") as demo:
    gr.Markdown(
        "# Style Finder\n"
        "Upload an outfit photo. We match it against a fashion catalog "
        "(ResNet50 + cosine similarity), then ask a vision LLM for a retail-style analysis.\n\n"
        "LLM: Groq vision / Ollama LLaVA via repo-root `.env`."
    )
    with gr.Row():
        with gr.Column():
            inp = gr.Image(type="pil", label="Your outfit")
            btn = gr.Button("Analyze", variant="primary")
            status = gr.Textbox(label="Status", interactive=False)
        with gr.Column():
            matched = gr.Image(type="pil", label="Closest catalog match")
            analysis = gr.Markdown(label="Analysis")
            catalog = gr.Markdown(label="Catalog rows")

    btn.click(
        fn=analyze_style,
        inputs=inp,
        outputs=[matched, analysis, catalog, status],
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7873, share=False)
