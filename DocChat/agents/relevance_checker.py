from __future__ import annotations

import re

from shared.llm import get_chat_llm
from utils.logging import logger


class RelevanceChecker:
    def __init__(self):
        self.llm = get_chat_llm(temperature=0)

    def check(self, question: str, retriever, k: int = 8) -> str:
        top_docs = retriever.invoke(question)
        if not top_docs:
            return "NO_MATCH"

        document_content = "\n\n".join(doc.page_content for doc in top_docs[:k])
        prompt = f"""You are an AI relevance checker between a user's question and provided document content.

Respond with ONLY one label: CAN_ANSWER, PARTIAL, or NO_MATCH.

1) CAN_ANSWER: passages fully answer the question
2) PARTIAL: topic is discussed but incomplete
3) NO_MATCH: topic not discussed

If passages mention the topic at all, prefer PARTIAL over NO_MATCH.

Question: {question}
Passages:
{document_content}
"""
        try:
            out = self.llm.invoke(prompt)
            text = (getattr(out, "content", None) or str(out)).strip().upper()
        except Exception as e:
            logger.error("Relevance check failed: %s", e)
            return "NO_MATCH"

        for label in ("CAN_ANSWER", "PARTIAL", "NO_MATCH"):
            if label in text:
                logger.info("Relevance: %s", label)
                return label
        # fallback regex
        m = re.search(r"CAN_ANSWER|PARTIAL|NO_MATCH", text)
        return m.group(0) if m else "NO_MATCH"
