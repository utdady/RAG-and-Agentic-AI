"""06 — RAG basics (Chroma + retrieve + QA). Advanced retrievers → sibling lab."""

from __future__ import annotations

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from _bootstrap import LABS, banner
from shared.embeddings import get_embedding_model, resolve_embedding_model
from shared.llm import get_llm_info

banner("06 RAG basics")
llm, _ = get_llm_info(temperature=0.1)
embeddings = get_embedding_model()
print(f"Embeddings: {resolve_embedding_model()}")

policies = LABS / "context_retrieval" / "data" / "companypolicies.txt"
if not policies.exists():
    import sys

    sys.path.insert(0, str(LABS / "context_retrieval"))
    from download_data import main as download_assets

    download_assets()

raw = policies.read_text(encoding="utf-8")
docs = [Document(page_content=raw, metadata={"source": policies.name})]
chunks = RecursiveCharacterTextSplitter(
    chunk_size=800, chunk_overlap=100
).split_documents(docs)
print(f"Chunks: {len(chunks)}")

store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="fundamentals_rag",
)
retriever = store.as_retriever(search_kwargs={"k": 3})

query = "What is the smoking policy?"
hits = retriever.invoke(query)
print(f"\nQuery: {query}")
for i, d in enumerate(hits, 1):
    print(f"  [{i}] {d.page_content[:160].replace(chr(10), ' ')}…")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer using only the context. If missing, say you don't know.\n\n"
            "Context:\n{context}",
        ),
        ("human", "{question}"),
    ]
)
context = "\n\n---\n\n".join(d.page_content for d in hits)
answer = llm.invoke(prompt.format_messages(context=context, question=query))
print("\nAnswer:", answer.content)

print(
    "\nFor MultiQuery / SelfQuery / ParentDocument, run:\n"
    "  python ../context_retrieval/lab.py"
)
