# Original lab notes (reference)

Source: IBM Skills Network-style notebook  
("Summarize Private Documents Using RAG, LangChain, and LLMs").

**Not the runnable lab** — Watsonx / older LangChain imports preserved for comparison.  
Runnable scripts: `01_*.py` … `03_*.py`.

---

## Flow (course)

1. Download `companyPolicies.txt` (wget) and inspect contents  
2. `TextLoader` → `CharacterTextSplitter(chunk_size=1000)` → `HuggingFaceEmbeddings` → Chroma  
3. Watsonx `Model` + `WatsonxLLM` (Mistral) → `RetrievalQA`  
   - “what is mobile policy?”  
   - “Can you summarize the document for me?”  
   - “Can I eat in company vehicles?”  
4. Second model wrap (same Mistral id in paste; lab names vary)  
5. Custom `PromptTemplate` for grounded answers  
6. `ConversationBufferMemory` + `ConversationalRetrievalChain` follow-ups  
   - mobile policy → list points → aim  
7. Interactive `while True` / `input()` chat  
8. Exercises: State of the Union download; `return_source_documents`; try another model id  

## Notable course quirks

- `return_message=True` → should be `return_messages=True`  
- Mix of `qa.invoke` and `qa({...})`  
- Variable named `flan_ul2_llm` but model id is Mistral  

## Pivot in this repo

| Course | Here |
|--------|------|
| WatsonxLLM | `shared.llm` |
| Default HuggingFaceEmbeddings | `shared.embeddings` (MiniLM) |
| wget policies | reuse `context_retrieval` data or download |
| CLI only | console scripts (+ optional REPL) |
