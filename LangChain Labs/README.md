# LangChain Labs

Curriculum labs for LangChain — not a Gradio/Flask product.

| Folder | What it covers |
|--------|----------------|
| [`fundamentals/`](fundamentals/) | Prompts, parsers, loaders, RAG basics, memory, LCEL chains, ReAct + manual tool-calling |
| [`prompt_engineering/`](prompt_engineering/) | Zero/one/few-shot, CoT, PromptTemplate + LCEL task patterns |
| [`document_rag/`](document_rag/) | Private-doc Chroma QA, custom prompts, conversational RAG |
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

Copy repo-root `env.example` → `.env` (preferred). Optional per-project `.env` overrides.

## Suggested order

1. `fundamentals/01` → `10` (core LangChain path)
2. `prompt_engineering/01` → `03` (deeper prompting; overlaps lightly with `fundamentals/03`)
3. `document_rag/01` → `03` (private-doc QA + conversational memory)
4. `context_retrieval/lab.py` (advanced retrievers; overlaps lightly with `06_rag_basics`)

## Reference

Original Watsonx notebook pastes live under each folder’s `reference/`.
