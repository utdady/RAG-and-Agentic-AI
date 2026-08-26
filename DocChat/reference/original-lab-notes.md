# DocChat / Multi-Agent RAG — original lab notes

Course: IBM Skills Network `zzpwx-docchat` (branches `1-start` / `2-final`).
Gradio DocChat with Docling ingestion, hybrid BM25+Chroma (Watsonx Slate),
and LangGraph agents (relevance / research / verification).

## Stack (course)

- Watsonx: Granite relevance, Llama research, Granite verify, Slate embeddings
  (`TRUNCATE_INPUT_TOKENS: 3` — known bad setting; not copied)
- `DocumentConverter` (Docling) → `MarkdownHeaderTextSplitter`
- Chunk pickle cache; EnsembleRetriever
- Gradio on port 5000 with `share=True` and example PDFs

## Workflow

`check_relevance` → (relevant? research : END) → `verify` →
(re_research | end) based on `Supported: NO` / `Relevant: NO` in report.

## This repo

Pivoted to `shared.llm` + MiniLM; local Gradio 7867; Docling optional with loader
fallback; `MAX_RESEARCH_LOOPS` to avoid infinite verify loops.
