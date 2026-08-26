# Original lab notes (vision reference)

Source: IBM Skills Network-style notebook cells  
(Gradio greet → BLIP captioning → ResNet18 ImageNet).

**Not the runnable demos** — Colab paths and course layout preserved for comparison.  
Runnable: `04_image_caption_blip.py`, `05_image_classify_resnet.py`.

---

```python
# Minimal Gradio greet (skipped in repo — see 01_add_numbers.py instead)
import gradio as gr

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

demo = gr.Interface(fn=greet, inputs=["text", "slider"], outputs=["text"])
demo.launch(server_name="127.0.0.1", server_port=7860)

# BLIP captioning
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

def generate_caption(image):
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.generate(**inputs)
    return processor.decode(outputs[0], skip_special_tokens=True)

def caption_image(image):
    try:
        return generate_caption(image)
    except Exception as e:
        return f"An error occurred: {str(e)}"

iface = gr.Interface(
    fn=caption_image,
    inputs=gr.Image(type="pil"),
    outputs="text",
    title="Image Captioning with BLIP",
    description="Upload an image to generate a caption.",
)
iface.launch(server_name="127.0.0.1", server_port=7860)

# ResNet18 ImageNet
import torch
import requests
from torchvision import transforms

model = torch.hub.load("pytorch/vision:v0.6.0", "resnet18", pretrained=True).eval()
response = requests.get("https://git.io/JJkYN")
labels = [l.strip() for l in response.text.split("\n") if l.strip()]
transform = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)

def predict(inp):
    inp = transform(inp).unsqueeze(0)
    with torch.no_grad():
        prediction = torch.nn.functional.softmax(model(inp)[0], dim=0)
    return {labels[i]: float(prediction[i]) for i in range(len(labels))}

gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Label(num_top_classes=3),
    examples=["/content/lion.jpg", "/content/cheetah.jpg"],
).launch()
```

## Pivot notes

- Greet demo soft-skipped (already covered by `01`)
- ResNet: use current `weights=` API; add Resize/CenterCrop before normalize
- Labels: pytorch hub `imagenet_classes.txt` instead of brittle `git.io` short link
- Colab example image paths removed (upload your own)
