"""04 — Image captioning with BLIP (Salesforce) + Gradio."""

from __future__ import annotations

import gradio as gr
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

print("Loading BLIP image-captioning-base (first run downloads weights)…")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)


def generate_caption(image: Image.Image) -> str:
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.generate(**inputs)
    return processor.decode(outputs[0], skip_special_tokens=True)


def caption_image(image: Image.Image | None) -> str:
    if image is None:
        return "Upload an image first."
    try:
        return generate_caption(image)
    except Exception as e:
        return f"An error occurred: {e}"


iface = gr.Interface(
    fn=caption_image,
    inputs=gr.Image(type="pil", label="Image"),
    outputs=gr.Textbox(label="Caption", lines=3),
    title="Image Captioning with BLIP",
    description="Upload an image to generate a caption (Salesforce/blip-image-captioning-base).",
    allow_flagging="never",
)

if __name__ == "__main__":
    iface.launch(server_name="127.0.0.1", server_port=7867, share=False)
