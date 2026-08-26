# DocChat

Gradio **multi-agent RAG**: upload documents → hybrid BM25 + Chroma → LangGraph  
**relevance → research → verification** (optional re-research).

- **LLM:** Groq / Ollama via [`../shared/llm.py`](../shared/llm.py)
- **Embeddings:** local MiniLM via [`../shared/embeddings.py`](../shared/embeddings.py)
- **Not Watsonx / Slate** — course DocChat used Granite, Llama, and Slate embeddings
- Related simpler app: [`../PDF QA Bot/`](../PDF%20QA%20Bot/) (single RetrievalQA, no verify loop)

## Setup

```powershell
cd DocChat
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env` with `GROQ_API_KEY` (preferred). `docling` is optional; without it, PDF/DOCX/TXT/MD still work via fallback loaders.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7867

## Pipeline

1. Chunk uploads (Docling→markdown headers when available; else PyPDF/docx/text)
2. Hybrid retriever (BM25 + Chroma)
3. Relevance agent: `CAN_ANSWER` / `PARTIAL` / `NO_MATCH`
4. Research agent drafts from retrieved context
5. Verification agent checks Supported/Relevant; may re-research (capped)

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
