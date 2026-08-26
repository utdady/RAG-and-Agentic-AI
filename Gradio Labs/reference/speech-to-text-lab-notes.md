# Original lab notes (speech-to-text reference)

Source: IBM Skills Network-style notebook  
(simple Whisper Gradio transcription; full meeting assistant is a separate lab).

**Not the runnable demos.**  
- STT-only: `07_speech_to_text.py`  
- Full pipeline: [`../../Meeting Assistant/`](../../Meeting%20Assistant/)

---

## Simple transcription (course)

```python
import torch
from transformers import pipeline
import gradio as gr

def transcript_audio(audio_file):
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-tiny.en",
        chunk_length_s=30,
    )
    return pipe(audio_file, batch_size=8)["text"]

iface = gr.Interface(
    fn=transcript_audio,
    inputs=gr.Audio(sources="upload", type="filepath"),
    outputs=gr.Textbox(),
    title="Audio Transcription App",
    description="Upload the audio file",
)
iface.launch(share=True)
```

## Meeting assistant (course) — already in repo

Whisper → ASCII cleanup → financial product term expansion → Watsonx Granite minutes/tasks → Gradio download.  
See `Meeting Assistant/reference/original-lab-notes.md`.

## Pivot

| Course | Here |
|--------|------|
| Rebuild pipeline every request | Load Whisper once at startup |
| Fixed `whisper-tiny.en` | `shared.llm.resolve_whisper_model()` (tier / `WHISPER_MODEL`) |
| `share=True` | Local `127.0.0.1:7870` |
| Full minutes app | Meeting Assistant (not duplicated) |
