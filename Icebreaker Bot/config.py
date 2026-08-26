"""Configuration settings for the Icebreaker Bot."""

from __future__ import annotations

import os
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ProxyCurl (optional — mock mode needs no key)
PROXYCURL_API_KEY = os.getenv("PROXYCURL_API_KEY", "").strip()

# Mock LinkedIn JSON (course asset)
MOCK_DATA_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "ZRe59Y_NJyn3hZgnF1iFYA/linkedin-profile-data.json"
)
MOCK_DATA_PATH = HERE / "data" / "linkedin-profile-data.json"
DEFAULT_MOCK_URL = "https://www.linkedin.com/in/leonkatsnelson/"

# Retrieval / chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "7"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

# Embeddings (local; override with EMBEDDING_MODEL)
EMBEDDING_MODEL = (
    os.getenv("EMBEDDING_MODEL", "").strip()
    or "sentence-transformers/all-MiniLM-L6-v2"
)

# Optional runtime LLM model override (Gradio / --model)
LLM_MODEL_OVERRIDE: str | None = None

INITIAL_FACTS_TEMPLATE = """
You are an AI assistant that provides detailed answers based on the provided context.

Context information is below:

{context_str}

Based on the context provided, list 3 interesting facts about this person's career or education.

Answer in detail, using only the information provided in the context.
"""

USER_QUESTION_TEMPLATE = """
You are an AI assistant that provides detailed answers to questions based on the provided context.

Context information is below:

{context_str}

Question: {query_str}

Answer in full details, using only the information provided in the context. If the answer is not available in the context, say "I don't know. The information is not available on the LinkedIn page."
"""
