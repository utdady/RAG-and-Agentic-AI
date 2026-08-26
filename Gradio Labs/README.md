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
| `07_speech_to_text.py` | 7870 | Whisper transcription only |
| `08_image_qa.py` | 7871 | Image Q&A (Groq vision / Ollama LLaVA) |
| `09_text_to_image_google.py` | 7872 | Text → image (Google Gemini) |

Full meeting minutes pipeline: [`../Meeting Assistant/`](../Meeting%20Assistant/).  
Multi-model chat: [`../Model Comparison Chat/`](../Model%20Comparison%20Chat/).

## Setup

```powershell
cd "Gradio Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional extras:

```powershell
pip install -r requirements-vision.txt      # 04, 05
pip install -r requirements-tts.txt         # 06
pip install -r requirements-asr.txt         # 07
pip install -r requirements-image-qa.txt    # 08
pip install -r requirements-google.txt      # 09
```

Copy repo-root `env.example` → `.env` (preferred). Optional per-project `.env` overrides.

- `03` / `06` / `08`: `GROQ_API_KEY` (and optional `GROQ_VISION_MODEL`)
- `09`: **`GOOGLE_API_KEY`** from [Google AI Studio](https://aistudio.google.com/apikey); optional `GEMINI_IMAGE_MODEL`

## Run

```powershell
python 08_image_qa.py
python 09_text_to_image_google.py
```

## Reference

- Gradio + chat: [`reference/original-lab-notes.md`](reference/original-lab-notes.md)
- Vision: [`reference/vision-lab-notes.md`](reference/vision-lab-notes.md)
- Storyteller: [`reference/storyteller-lab-notes.md`](reference/storyteller-lab-notes.md)
- Speech-to-text: [`reference/speech-to-text-lab-notes.md`](reference/speech-to-text-lab-notes.md)
- Image Q&A + Google T2I: [`reference/image-gen-qa-lab-notes.md`](reference/image-gen-qa-lab-notes.md)
