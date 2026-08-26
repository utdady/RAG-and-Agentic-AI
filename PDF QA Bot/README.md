# PDF QA Bot

Gradio RAG chatbot: upload a PDF, ask questions answered from that document only.

- **LLM:** Groq / Ollama via [`../shared/llm.py`](../shared/llm.py)
- **Embeddings:** local MiniLM via [`../shared/embeddings.py`](../shared/embeddings.py)
- **Store:** ephemeral Chroma (cached per uploaded file)

## Setup

```powershell
cd "PDF QA Bot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy repo-root `env.example` → `.env` (preferred). Optional per-project `.env` overrides.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7863 — upload a `.pdf`, type a question, submit.

## Notes

- Index is rebuilt once per file path/mtime, then reused for follow-up questions.
- Course lab used Watsonx Mistral + Slate and `TRUNCATE_INPUT_TOKENS: 3` (typo) — not copied here.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
