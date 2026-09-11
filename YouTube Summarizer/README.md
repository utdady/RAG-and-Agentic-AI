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
- Embedding model weights download on first **Ask** (Q&A), not on summarize.
## Cloud / Render notes

YouTube often returns **403** to datacenter IPs. Set one of these on the API host:

- `YOUTUBE_PROXY_URL` — HTTP(S) proxy URL used by transcript API + yt-dlp
- `WEBSHARE_PROXY_USERNAME` + `WEBSHARE_PROXY_PASSWORD` — [Webshare](https://www.webshare.io/) residential proxies via `youtube-transcript-api`

Without a proxy, the hub falls back to yt-dlp captions, then Groq Whisper on downloaded audio — those paths also fail when YouTube blocks the server IP.

- Original IBM / Watsonx lab paste: [`reference/original-lab-notes.md`](reference/original-lab-notes.md).
