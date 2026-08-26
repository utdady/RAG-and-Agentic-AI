# Gradio Labs

Intro demos for Gradio interfaces — not a product chatbot.

| Script | Port | What it shows |
|--------|------|----------------|
| `01_add_numbers.py` | 7864 | `gr.Interface` + numbers |
| `02_sentence_builder.py` | 7865 | Slider, dropdown, checkbox, radio, examples |
| `03_simple_chat.py` | 7866 | Text → Groq/Ollama via [`../shared/llm.py`](../shared/llm.py) |
| `04_image_caption_blip.py` | 7867 | BLIP image captioning |
| `05_image_classify_resnet.py` | 7868 | ResNet18 ImageNet top-3 |
| `06_storyteller.py` | 7869 | Educational story + gTTS narration |

For a real multi-model chat UI, use [`../Model Comparison Chat/`](../Model%20Comparison%20Chat/).

## Setup

```powershell
cd "Gradio Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional extras:

```powershell
pip install -r requirements-vision.txt   # 04, 05
pip install -r requirements-tts.txt      # 06
```

Copy `env.example` → `.env` (needed for `03` / `06`), or reuse `Meeting Assistant/.env`.

## Run

```powershell
python 01_add_numbers.py
python 02_sentence_builder.py
python 03_simple_chat.py
python 04_image_caption_blip.py
python 05_image_classify_resnet.py
python 06_storyteller.py
```

First BLIP/ResNet run downloads model weights. Storyteller needs network for gTTS.

## Reference

- Gradio + chat: [`reference/original-lab-notes.md`](reference/original-lab-notes.md)
- Vision: [`reference/vision-lab-notes.md`](reference/vision-lab-notes.md)
- Storyteller: [`reference/storyteller-lab-notes.md`](reference/storyteller-lab-notes.md)
