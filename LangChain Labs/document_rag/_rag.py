"""Shared ingest helpers for document RAG demos."""

from __future__ import annotations

from pathlib import Path

import requests
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter

from _bootstrap import HERE, LABS
from shared.embeddings import get_embedding_model

# Prefer sibling context_retrieval asset; fall back to course URL
POLICIES_SIBLING = LABS / "context_retrieval" / "data" / "companypolicies.txt"
POLICIES_LOCAL = HERE / "data" / "companypolicies.txt"
POLICIES_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "6JDbUb_L3egv_eOkouY71A.txt"
)
SOTU_LOCAL = HERE / "data" / "stateOfUnion.txt"
SOTU_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "XVnuuEg94sAE4S_xAsGxBA.txt"
)


def _download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    print(f"Downloading {dest.name}…")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


def ensure_policies() -> Path:
    if POLICIES_SIBLING.exists() and POLICIES_SIBLING.stat().st_size > 0:
        return POLICIES_SIBLING
    # Try sibling download helper
    try:
        import sys

        sys.path.insert(0, str(LABS / "context_retrieval"))
        from download_data import main as download_cr

        download_cr()
        if POLICIES_SIBLING.exists():
            return POLICIES_SIBLING
    except Exception:
        pass
    return _download(POLICIES_URL, POLICIES_LOCAL)


def ensure_state_of_union() -> Path:
    return _download(SOTU_URL, SOTU_LOCAL)


def build_vectorstore(path: Path, collection_name: str = "doc_rag") -> Chroma:
    docs = TextLoader(str(path), encoding="utf-8").load()
    chunks = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0,
    ).split_documents(docs)
    print(f"Loaded {path.name}: {len(chunks)} chunks")
    return Chroma.from_documents(
        chunks,
        get_embedding_model(),
        collection_name=collection_name,
    )
