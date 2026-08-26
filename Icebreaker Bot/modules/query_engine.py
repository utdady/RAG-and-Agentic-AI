"""Query the indexed LinkedIn profile (icebreaker facts + Q&A)."""

from __future__ import annotations

import logging
from typing import Any

from llama_index.core import PromptTemplate, VectorStoreIndex

from modules.llm_interface import create_llm
import config

logger = logging.getLogger(__name__)


def generate_initial_facts(index: VectorStoreIndex) -> str:
    """List 3 interesting career/education facts grounded in the profile."""
    try:
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


def answer_user_query(index: VectorStoreIndex, user_query: str) -> Any:
    """Answer a user question using only retrieved LinkedIn context."""
    try:
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
