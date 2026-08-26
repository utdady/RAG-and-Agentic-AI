# LinkedIn Icebreaker Bot

Gradio + CLI RAG over a LinkedIn profile (mock JSON by default, optional ProxyCurl).

- **LLM:** Groq / Ollama via [`../shared/llama_index_llm.py`](../shared/llama_index_llm.py)
- **Embeddings:** local MiniLM (LlamaIndex HuggingFaceEmbedding)
- **Not Watsonx / Slate** — course notebook pivoted off IBM Granite + Slate

## Setup

```powershell
cd "Icebreaker Bot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `env.example` → `.env`, or reuse `Meeting Assistant/.env` for `GROQ_API_KEY`.

## Run

**Gradio (recommended):**

```powershell
python app.py
```

Open http://127.0.0.1:7862 — leave **Use Mock Data** checked for the course sample profile.

**CLI:**

```powershell
python main.py --mock
python main.py --url https://www.linkedin.com/in/someone/ --api-key YOUR_PROXYCURL_KEY
```

## Flow

1. Load mock LinkedIn JSON (or ProxyCurl scrape)
2. Chunk → embed → in-memory `VectorStoreIndex`
3. Generate 3 icebreaker facts
4. Chat Q&A grounded on the profile (says “I don’t know…” if missing)

## Notes

- Live ProxyCurl can return sensitive fields; mock mode is the default for demos.
- Original lab used `truncate_input_tokens=3` on Slate — **not** copied here.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
