# YouTube Summarizer & QA (RAG)

Fetch an English YouTube transcript, summarize it, and answer questions with **FAISS + local embeddings** and **Groq / Ollama** (via [`../shared/`](../shared/)).

## Setup

1. Create a venv (recommended separate from Meeting Assistant if pins clash):

```powershell
cd "YouTube Summarizer"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy repo-root `env.example` → `.env` and set `GROQ_API_KEY` (preferred). Optional per-project `.env` overrides.

3. For local-only LLM: install [Ollama](https://ollama.com) and leave `GROQ_API_KEY` empty.

4. Run:

```powershell
python app.py
```

Open `http://127.0.0.1:7860`.

## Pipeline

1. Parse video id (`watch?v=`, `youtu.be/`, `shorts/`)
2. Prefer manual English transcript, else auto-generated
3. Format lines as `Text: … Start: …`
4. **Summarize:** full(ish) transcript → chat LLM
5. **Ask:** chunk → MiniLM embeddings → FAISS top-k → chat LLM

Transcript + FAISS index are **cached per video id** for the process lifetime.

## Notes

- Videos without an English transcript will fail gracefully.
- First run downloads the embedding model weights.
- Original IBM / Watsonx lab paste: [`reference/original-lab-notes.md`](reference/original-lab-notes.md).
