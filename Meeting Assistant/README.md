# AI Meeting Assistant

Whisper (local) + **Groq** (free API) or **Ollama** (local fallback) + Gradio.

Pipeline: upload audio → transcribe → optional financial-term cleanup → meeting minutes & tasks → downloadable `.txt`.

LLM helpers live in [`../shared/`](../shared/) so other projects can reuse the same provider logic.

## Setup (Windows)

1. Install [ffmpeg](https://ffmpeg.org/download.html) and ensure it is on your `PATH`.
2. Pick an LLM backend:
   - **Groq (recommended):** free key from [console.groq.com/keys](https://console.groq.com/keys)
   - **Ollama (no key):** install [Ollama](https://ollama.com), then e.g. `ollama pull llama3.2:3b`
3. Create a venv and install deps:

```powershell
cd "Meeting Assistant"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Copy repo-root `env.example` → `.env` and set `GROQ_API_KEY` (or leave it empty to use Ollama). Optional `Meeting Assistant/.env` only for project-specific overrides.

5. (Optional) download the lab sample audio:

```powershell
python download_sample.py
```

6. Run:

```powershell
python app.py
```

Open `http://127.0.0.1:5000`. Startup logs which provider/model and Whisper id were chosen.

## Provider selection

| `LLM_PROVIDER` | Behavior |
|----------------|----------|
| `auto` (default) | Groq if `GROQ_API_KEY` is set, else Ollama |
| `groq` | Require `GROQ_API_KEY` |
| `ollama` | Local only |

### Ollama / Whisper auto-tier

When `OLLAMA_MODEL` / `WHISPER_MODEL` are unset, `shared.llm` picks from machine RAM/GPU:

| Tier | Ollama (suggested) | Whisper |
|------|--------------------|---------|
| low | `llama3.2:1b` | `whisper-tiny.en` |
| mid | `llama3.2:3b` | `whisper-base.en` |
| high | `llama3.1:8b` | `whisper-small.en` |

Already-pulled Ollama models are preferred when they fit the tier. Force with `HARDWARE_TIER` or explicit model env vars.

## Notes

- Whisper is loaded once at startup.
- Set `ENABLE_PRODUCT_ASSISTANT=true` for earnings-call acronym normalization (extra LLM call).
- Original IBM lab paste (Watsonx, not runnable): [`reference/original-lab-notes.md`](reference/original-lab-notes.md).
