# Advanced Retrievers (LlamaIndex)

Exploratory lab: compare vector, BM25, document-summary, auto-merging, recursive, query-fusion, and hybrid retrieval — then a tiny RAG pipeline.

**Not a Gradio app.** Run as a script and read the console output.

LLM via [`../shared/llama_index_llm.py`](../shared/llama_index_llm.py) (Groq / Ollama). Embeddings: local `BAAI/bge-small-en-v1.5`.

## Setup

```powershell
cd "Advanced Retrievers LlamaIndex"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy repo-root `env.example` → `.env` (preferred). Optional per-project `.env` overrides.

Optional: `SKIP_DOC_SUMMARY=true` to avoid extra LLM calls when building the summary index.

## Run

```powershell
python lab.py
```

## Sections

1. Vector index retriever  
2. BM25 retriever  
3. Document summary (LLM + embedding)  
4. Auto-merging retriever  
5. Recursive retriever  
6. Query fusion (RRF / relative / dist-based)  
7. Hybrid vector+BM25  
8. Mini production RAG pipeline  

## Reference

Original Watsonx lab paste: [`reference/original-lab-notes.md`](reference/original-lab-notes.md).
