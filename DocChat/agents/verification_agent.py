from __future__ import annotations

from typing import Dict, List

from langchain_core.documents import Document

from shared.llm import get_chat_llm
from utils.logging import logger


class VerificationAgent:
    def __init__(self):
        self.llm = get_chat_llm(temperature=0)

    def check(self, answer: str, documents: List[Document]) -> Dict:
        context = "\n\n".join(doc.page_content for doc in documents)
        prompt = f"""Verify the answer against the context. Respond in EXACTLY this format:

Supported: YES/NO
Unsupported Claims: [item1, item2, ...]
Contradictions: [item1, item2, ...]
Relevant: YES/NO
Additional Details: ...

Answer: {answer}

Context:
{context}
"""
        try:
            out = self.llm.invoke(prompt)
            report = (getattr(out, "content", None) or str(out)).strip()
        except Exception as e:
            logger.error("VerificationAgent failed: %s", e)
            report = (
                "Supported: NO\nUnsupported Claims: []\nContradictions: []\n"
                "Relevant: NO\nAdditional Details: model error"
            )
        if not report:
            report = (
                "Supported: NO\nUnsupported Claims: []\nContradictions: []\n"
                "Relevant: NO\nAdditional Details: empty model response"
            )
        return {"verification_report": report, "context_used": context}
