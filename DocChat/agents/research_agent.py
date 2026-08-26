from __future__ import annotations

from typing import Dict, List

from langchain_core.documents import Document

from shared.llm import get_chat_llm
from utils.logging import logger


class ResearchAgent:
    def __init__(self):
        self.llm = get_chat_llm(temperature=0.3)

    def generate(self, question: str, documents: List[Document]) -> Dict:
        context = "\n\n".join(doc.page_content for doc in documents)
        prompt = f"""You are an AI assistant that answers using ONLY the provided context.
Be clear and factual. If the context is insufficient, say so.

Question: {question}

Context:
{context}

Answer:
"""
        try:
            out = self.llm.invoke(prompt)
            draft = (getattr(out, "content", None) or str(out)).strip()
        except Exception as e:
            logger.error("ResearchAgent failed: %s", e)
            draft = "I cannot answer this question based on the provided documents."
        if not draft:
            draft = "I cannot answer this question based on the provided documents."
        return {"draft_answer": draft, "context_used": context}
