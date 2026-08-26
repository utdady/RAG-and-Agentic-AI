# Document RAG (LangChain Labs)

Summarize / Q&A over private text with Chroma + conversational memory.

Course: “Summarize Private Documents Using RAG, LangChain, and LLMs”  
(Watsonx → Groq/Ollama + local MiniLM).

Reuses [`../context_retrieval/data/companypolicies.txt`](../context_retrieval/data/companypolicies.txt) when present.

## Run

Same venv as `LangChain Labs/`:

```powershell
cd "LangChain Labs\document_rag"
python 01_ingest_and_qa.py
python 02_custom_prompt.py
python 03_conversational_rag.py --no-repl   # scripted only
python 03_conversational_rag.py --sotu      # also try State of the Union text
```

| Script | Topic |
|--------|--------|
| `01_ingest_and_qa.py` | TextLoader → Chroma → RetrievalQA (+ sources) |
| `02_custom_prompt.py` | Grounded PromptTemplate (“don’t make up answers”) |
| `03_conversational_rag.py` | ConversationalRetrievalChain + follow-ups / REPL |

For Gradio PDF upload UX → [`../../PDF QA Bot/`](../../PDF%20QA%20Bot/).

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
