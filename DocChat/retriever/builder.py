"""Hybrid BM25 + Chroma retriever (local MiniLM embeddings)."""

from __future__ import annotations

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma

from config import settings
from shared.embeddings import get_embedding_model
from utils.logging import logger


class RetrieverBuilder:
    def __init__(self):
        self.embeddings = get_embedding_model()

    def build_hybrid_retriever(self, docs):
        settings.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
        try:
            vector_store = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=str(settings.CHROMA_DB_PATH),
            )
            bm25 = BM25Retriever.from_documents(docs)
            bm25.k = settings.VECTOR_SEARCH_K
            vector_retriever = vector_store.as_retriever(
                search_kwargs={"k": settings.VECTOR_SEARCH_K}
            )
            hybrid = EnsembleRetriever(
                retrievers=[bm25, vector_retriever],
                weights=settings.HYBRID_RETRIEVER_WEIGHTS,
            )
            logger.info("Hybrid retriever ready (%s docs)", len(docs))
            return hybrid
        except Exception as e:
            logger.error("Failed to build hybrid retriever: %s", e)
            raise
