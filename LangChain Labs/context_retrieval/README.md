# LangChain Context Retrieval

Lab: smarter Chroma search patterns with LangChain — similarity, MMR, score threshold, MultiQuery, SelfQuery, ParentDocument.

**Not a Gradio app.** Console script.

- LLM: Groq / Ollama via [`../../shared/llm.py`](../../shared/llm.py)
- Embeddings: local MiniLM via [`../../shared/embeddings.py`](../../shared/embeddings.py)
- Sibling curriculum: [`../fundamentals/`](../fundamentals/)

## Setup

```powershell
cd "LangChain Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy repo-root `env.example` → `.env` (preferred). Optional per-project `.env` overrides.

```powershell
cd context_retrieval
```

## Run

```powershell
python download_data.py   # optional; lab.py also downloads if missing
python lab.py
```

Assets land in `data/` (company policies + LangChain paper PDF).

## Sections

1. Basic Chroma retrievers on policies (`k`, MMR, threshold)  
2. MultiQuery on the LangChain paper  
3. SelfQuery on movie docs with metadata filters  
4. ParentDocument on policies (child hit vs parent return)  
5. Plain `k=2` baseline for smoking policy  

## Reference

Original Watsonx notebook paste: [`reference/original-lab-notes.md`](reference/original-lab-notes.md).
