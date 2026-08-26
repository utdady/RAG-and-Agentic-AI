"""01 — Ingest private text → Chroma → RetrievalQA (Q&A + summarize)."""

from __future__ import annotations

from langchain.chains import RetrievalQA

from _bootstrap import banner
from _rag import build_vectorstore, ensure_policies
from shared.embeddings import resolve_embedding_model
from shared.llm import get_llm_info

banner("01 Ingest and QA")
llm, info = get_llm_info(temperature=0.5)
print(f"LLM={info.provider}:{info.model}")
print(f"Embeddings={resolve_embedding_model()}\n")

path = ensure_policies()
store = build_vectorstore(path, collection_name="policies_qa")
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=store.as_retriever(),
    return_source_documents=False,
)

for query in [
    "what is mobile policy?",
    "Can you summarize the document for me?",
    "Can I eat in company vehicles?",
]:
    print(f"\nQ: {query}")
    result = qa.invoke(query)
    answer = result["result"] if isinstance(result, dict) else result
    print(f"A: {answer}")

# Source documents demo
print("\n--- with source_documents ---")
qa_src = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=store.as_retriever(),
    return_source_documents=True,
)
src_result = qa_src.invoke("Can I smoke in company vehicles?")
print("A:", src_result["result"])
if src_result.get("source_documents"):
    print("\nTop source chunk:\n", src_result["source_documents"][0].page_content[:400], "…")
