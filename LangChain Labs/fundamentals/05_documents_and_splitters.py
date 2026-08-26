"""05 — Document loaders + text splitters (PDF / text; web optional)."""

from __future__ import annotations

import sys

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

from _bootstrap import LABS, banner

banner("05 Documents and splitters")

# Reuse assets from context_retrieval sibling when present
DATA = LABS / "context_retrieval" / "data"

policies = DATA / "companypolicies.txt"
pdf = DATA / "langchain-paper.pdf"

if not policies.exists() or not pdf.exists():
    print("Missing context_retrieval assets — downloading…")
    sys.path.insert(0, str(LABS / "context_retrieval"))
    from download_data import main as download_assets

    download_assets()

print(f"Policies: {policies}")
print(f"PDF: {pdf}")

# Text loader
text_docs = TextLoader(str(policies), encoding="utf-8").load()
print(f"\nTextLoader: {len(text_docs)} doc(s), "
      f"{len(text_docs[0].page_content)} chars")

# PDF loader (first few pages enough for demo)
pdf_docs = PyPDFLoader(str(pdf)).load()
print(f"PyPDFLoader: {len(pdf_docs)} page(s)")

# Splitters
char = CharacterTextSplitter(chunk_size=500, chunk_overlap=50, separator="\n")
recur = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

char_chunks = char.split_documents(text_docs)
recur_chunks = recur.split_documents(text_docs)
print(f"\nCharacterTextSplitter → {len(char_chunks)} chunks")
print(f"RecursiveCharacterTextSplitter → {len(recur_chunks)} chunks")
print("\nSample recursive chunk:\n", recur_chunks[0].page_content[:300], "…")
