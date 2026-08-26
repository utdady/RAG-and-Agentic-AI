# LangChain Fundamentals

Runnable scripts for **Build Smarter AI Apps: Empower LLMs with LangChain**.

Watsonx / Slate → **Groq/Ollama** + **local MiniLM**. Prefer LCEL over deprecated `LLMChain` / `ConversationChain`.

## Run (from this folder, venv already set up in `LangChain Labs/`)

```powershell
cd "LangChain Labs\fundamentals"
python 01_llm_and_messages.py
python 02_temperature_compare.py
python 03_prompts.py
python 04_output_parsers.py
python 05_documents_and_splitters.py
python 06_rag_basics.py
python 07_memory.py
python 08_chains_lcel.py
python 09_agents.py
```

`05` / `06` reuse PDFs/text from [`../context_retrieval/data`](../context_retrieval/data) (auto-download if missing).

Advanced Chroma retrievers (MultiQuery, SelfQuery, ParentDocument) → [`../context_retrieval/`](../context_retrieval/).  
Deeper zero/one/few-shot + CoT → [`../prompt_engineering/`](../prompt_engineering/).

## Scripts

| Script | Topic |
|--------|--------|
| `01_llm_and_messages.py` | Chat model + System/Human/AI messages |
| `02_temperature_compare.py` | Creative vs precise temperature |
| `03_prompts.py` | PromptTemplate, ChatPromptTemplate, MessagesPlaceholder |
| `04_output_parsers.py` | CSV list + JSON/Pydantic |
| `05_documents_and_splitters.py` | Text/PDF loaders + splitters |
| `06_rag_basics.py` | Chroma retrieve + grounded QA |
| `07_memory.py` | RunnableWithMessageHistory |
| `08_chains_lcel.py` | LCEL pipes (incl. sequential) |
| `09_agents.py` | ReAct tools (safe calculator) |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
