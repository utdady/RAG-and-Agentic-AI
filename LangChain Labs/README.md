# LangChain Labs

Curriculum labs for LangChain — not a Gradio/Flask product.

| Folder | What it covers |
|--------|----------------|
| [`fundamentals/`](fundamentals/) | Prompts, parsers, loaders, RAG basics, memory, LCEL chains, ReAct agents |
| [`context_retrieval/`](context_retrieval/) | Chroma retrievers: MMR, MultiQuery, SelfQuery, ParentDocument |

**LLM:** Groq / Ollama via [`../shared/llm.py`](../shared/llm.py)  
**Embeddings:** local MiniLM via [`../shared/embeddings.py`](../shared/embeddings.py)

## Setup

```powershell
cd "LangChain Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `env.example` → `.env`, or reuse `Meeting Assistant/.env`.

## Suggested order

1. `fundamentals/01` → `09` (core LangChain path)
2. `context_retrieval/lab.py` (advanced retrievers; overlaps lightly with `06_rag_basics`)

## Reference

Original Watsonx notebook pastes live under each folder’s `reference/`.
