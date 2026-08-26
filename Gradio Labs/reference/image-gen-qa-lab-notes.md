# Original lab notes (image gen + image Q&A)

Sources: IBM Skills Network-style notebooks  
(OpenAI / Watsonx text→image and Watsonx multimodal image→text).

**Runnable demos**
- `08_image_qa.py` — VQA (Groq vision / Ollama; BLIP fallback)
- `09_text_to_image_google.py` — Gemini image gen (`GOOGLE_API_KEY`)

---

## Text → image (course used OpenAI)

```python
from openai import OpenAI
import base64
from IPython import display

client = OpenAI()
response = client.images.generate(
    model="gpt-image-2",  # verify current OpenAI image model ids
    prompt="a white Siamese cat",
    size="1024x1024",
    n=1,
)
image_bytes = base64.b64decode(response.data[0].b64_json)
display.display(display.Image(data=image_bytes, width=512))
```

**Pivot:** Google Gemini Flash Image via `google-genai` + `GOOGLE_API_KEY` (not OpenAI paid image API).

## Image → text / VQA (course used Watsonx Mistral chat)

- Download course sample PNGs from Cloud Object Storage
- `model.chat` with `image_url` data-URI base64
- Queries: describe, count cars, damage severity, sodium / cholesterol on label

**Pivot:** Groq vision model or Ollama LLaVA with LangChain multimodal `HumanMessage`.

## Env

```
GOOGLE_API_KEY=
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
OLLAMA_VISION_MODEL=llava
```
