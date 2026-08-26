# Model Comparison Chat

Flask app to compare LLM slots (fast / balanced / quality) with structured JSON output:
`summary`, `sentiment` (0–100), `response`, plus latency.

Standalone product (not clubbed with Meeting Assistant / YouTube).  
LLM backends: **Groq** and/or **Ollama** via [`../shared/llm.py`](../shared/llm.py) provider resolution — no Watsonx.

## Setup

```powershell
cd "Model Comparison Chat"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy repo-root `env.example` → `.env` and set `GROQ_API_KEY` (preferred).

Without a Groq key, each slot falls back to its Ollama model (pull those models first).

## Run

```powershell
python app.py
```

Open `http://127.0.0.1:5001`.

## Model slots (lab names kept)

| UI key | Default Groq model | Default Ollama |
|--------|--------------------|----------------|
| `llama` | `llama-3.1-8b-instant` | `llama3.2:3b` |
| `granite` | `gemma2-9b-it` (balanced) | `gemma2:2b` |
| `mistral` | `llama-3.3-70b-versatile` | `mistral:7b` |

Override with `LLAMA_MODEL`, `GRANITE_MODEL`, `MISTRAL_MODEL`, etc. in `.env`.

True IBM Granite / Mistral Small on Watsonx needs an IBM key; this port teaches **choose by speed/quality/cost** using models you can run for free.

## Layout

- `app.py` — Flask routes
- `models.py` — chains + JSON parser
- `config.py` — env + slot map
- `templates/` / `static/` — chat UI
- `reference/` — LLM theory + original Watsonx lab notes

## Compare models

Send the same customer question with each slot selected and compare:
- response quality
- sentiment/summary usefulness
- `duration` (seconds)
