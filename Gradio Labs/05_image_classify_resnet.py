"""05 — ImageNet classification with ResNet18 + Gradio Label."""

from __future__ import annotations

import gradio as gr
import requests
import torch
from torchvision import transforms

print("Loading ResNet18 (torch.hub)…")
try:
    model = torch.hub.load(
        "pytorch/vision:v0.10.0",
        "resnet18",
        weights="DEFAULT",
    ).eval()
except TypeError:
    model = torch.hub.load(
        "pytorch/vision:v0.10.0",
        "resnet18",
        pretrained=True,
    ).eval()


# Human-readable ImageNet labels (same gist the course used via git.io)
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
try:
    response = requests.get(LABELS_URL, timeout=30)
    response.raise_for_status()
    labels = [line.strip() for line in response.text.splitlines() if line.strip()]
except Exception:
    # Fallback short list if offline — indices won't match ImageNet; warn in UI
    labels = [f"class_{i}" for i in range(1000)]
    print("Warning: could not download ImageNet labels; using placeholders.")

transform = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            [0.485, 0.456, 0.406],
            [0.229, 0.224, 0.225],
        ),
    ]
)


def predict(inp):
    if inp is None:
        return {}
    batch = transform(inp).unsqueeze(0)
    with torch.no_grad():
        prediction = torch.nn.functional.softmax(model(batch)[0], dim=0)
    n = min(len(labels), prediction.numel())
    return {labels[i]: float(prediction[i]) for i in range(n)}


demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil", label="Image"),
    outputs=gr.Label(num_top_classes=3, label="Top classes"),
    title="Image Classification (ResNet18)",
    description="Upload an image for ImageNet top-3 predictions.",
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7868, share=False)
