# Original lab notes (reference)

Source: IBM Skills Network-style project  
("Build an AI Icebreaker Bot with IBM Granite 3.0 & LlamaIndex").

**Not the runnable app** — Watsonx Granite / Slate / ProxyCurl notebook flow preserved for comparison.  
Runnable code in this folder uses Groq/Ollama + local MiniLM.

---

## Setup (course)

```bash
wget -qO- https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/bZyisII_msBvxphC0H0MlQ/icebreaker.tar | tar -xf -
cd icebreaker
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Config (Watsonx)

- `WATSONX_URL`, `WATSONX_PROJECT_ID`
- `LLM_MODEL_ID = ibm/granite-4-h-small`
- `EMBEDDING_MODEL_ID = ibm/slate-125m-english-rtrvr-v2` (lab used `truncate_input_tokens=3` — typo)
- `PROXYCURL_API_KEY`, mock JSON URL
- `CHUNK_SIZE` 400–500, `SIMILARITY_TOP_K` 5–7
- Templates: `INITIAL_FACTS_TEMPLATE`, `USER_QUESTION_TEMPLATE`

## Modules (course)

1. **data_extraction** — mock JSON download or ProxyCurl `nubela.co/proxycurl/api/v2/linkedin`; clean empty fields; drop `people_also_viewed` / `certifications`
2. **data_processing** — `Document(json)` → `SentenceSplitter` → `VectorStoreIndex` with Watsonx embeddings; verify embeddings
3. **llm_interface** — `WatsonxEmbeddings` / `WatsonxLLM`; `change_llm_model`
4. **query_engine** — `generate_initial_facts`, `answer_user_query` with LlamaIndex `PromptTemplate` + query engine
5. **main.py** — CLI argparse `--url` / `--api-key` / `--mock` / `--model` + REPL chat
6. **Gradio** — process tab + chat tab; in-memory `active_indices[session_id]`

## Run (course)

```bash
python main.py --mock
python main.py --url https://www.linkedin.com/in/johndoe/ --api-key YOUR_API_KEY
# Gradio: server 127.0.0.1:5000, share=True
```

## Pivot in this repo

| Course | This folder |
|--------|-------------|
| WatsonxLLM / Granite | `shared.llama_index_llm` (Groq/Ollama) |
| Slate embeddings | Local MiniLM via LlamaIndex HuggingFaceEmbedding |
| Gradio port 5000 | `7862` |
| ProxyCurl required for live | Optional; **mock default** |
