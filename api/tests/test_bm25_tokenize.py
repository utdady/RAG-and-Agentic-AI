from __future__ import annotations

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

from shared.bm25_tokenize import _tokenize


def test_tokenize_lowercases_and_splits_words():
    assert _tokenize("COVID-19 outbreak") == ["covid", "19", "outbreak"]
    assert _tokenize("BRCA1 mutations") == ["brca1", "mutations"]


def test_bm25_retrieval_is_case_insensitive():
    docs = [
        Document(page_content="The capital of France is Paris."),
        Document(page_content="Berlin is the capital of Germany."),
    ]
    retriever = BM25Retriever.from_documents(docs, preprocess_func=_tokenize)
    retriever.k = 1

    upper = retriever.invoke("FRANCE capital")
    lower = retriever.invoke("france capital")

    assert upper[0].page_content == lower[0].page_content