"""Query the indexed LinkedIn profile (icebreaker facts + Q&A)."""

from __future__ import annotations

import json
import logging
from typing import Any, Union

from llama_index.core import PromptTemplate, VectorStoreIndex

from modules.llm_interface import create_llm
import config

logger = logging.getLogger(__name__)

ProfileIndex = Union[VectorStoreIndex, "TextProfileIndex"]


class TextProfileIndex:
    """Lightweight profile context without MiniLM embeddings (hub-safe)."""

    def __init__(self, profile_data: dict[str, Any], max_chars: int = 14000):
        self.context = json.dumps(profile_data, indent=2, ensure_ascii=False)[
            :max_chars
        ]


def _complete(prompt: str) -> str:
    llm = create_llm(temperature=0.0)
    resp = llm.complete(prompt)
    return (getattr(resp, "text", None) or str(resp)).strip()


def generate_initial_facts(index: ProfileIndex) -> str:
    """List 3 interesting career/education facts grounded in the profile."""
    try:
        if isinstance(index, TextProfileIndex):
            prompt = (
                "You are an AI assistant that provides detailed answers based on "
                "the provided LinkedIn profile context.\n\n"
                f"Context:\n{index.context}\n\n"
                "List 3 interesting facts about this person's career or education. "
                "Use only the information provided."
            )
            return _complete(prompt) or "Failed to generate initial facts."

        llm = create_llm(temperature=0.0)
        facts_prompt = PromptTemplate(template=config.INITIAL_FACTS_TEMPLATE)
        query_engine = index.as_query_engine(
            streaming=False,
            similarity_top_k=config.SIMILARITY_TOP_K,
            llm=llm,
            text_qa_template=facts_prompt,
        )
        response = query_engine.query(
            "Provide three interesting facts about this person's career or education."
        )
        return str(response)
    except Exception as e:
        logger.error("Error in generate_initial_facts: %s", e)
        return "Failed to generate initial facts."


def answer_user_query(index: ProfileIndex, user_query: str) -> Any:
    """Answer a user question using only retrieved LinkedIn context."""
    try:
        if isinstance(index, TextProfileIndex):
            prompt = (
                "You are an AI assistant that answers questions using only the "
                "LinkedIn profile context below. If the answer is not available, "
                'say "I don\'t know. The information is not available on the '
                'LinkedIn page."\n\n'
                f"Context:\n{index.context}\n\n"
                f"Question: {user_query}\n\nAnswer:"
            )
            text = _complete(prompt) or "Failed to get an answer."

            class _Ok:
                response = text

            return _Ok()

        llm = create_llm(temperature=0.0)
        question_prompt = PromptTemplate(template=config.USER_QUESTION_TEMPLATE)
        query_engine = index.as_query_engine(
            streaming=False,
            similarity_top_k=config.SIMILARITY_TOP_K,
            llm=llm,
            text_qa_template=question_prompt,
        )
        return query_engine.query(user_query)
    except Exception as e:
        logger.error("Error in answer_user_query: %s", e)

        class _Err:
            response = "Failed to get an answer."

        return _Err()
