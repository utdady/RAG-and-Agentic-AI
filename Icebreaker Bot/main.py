"""CLI for the LinkedIn Icebreaker Bot."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shared.env_load import load_env

load_env(HERE)
import config
from modules.data_extraction import extract_linkedin_profile
from modules.data_processing import (
    create_vector_database,
    split_profile_data,
    verify_embeddings,
)
from modules.llm_interface import change_llm_model
from modules.query_engine import answer_user_query, generate_initial_facts
from shared.llama_index_llm import describe_llama_index_llm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)
logger = logging.getLogger(__name__)


def process_linkedin(linkedin_url: str, api_key: str | None = None, mock: bool = False) -> None:
    profile_data = extract_linkedin_profile(linkedin_url, api_key, mock=mock)
    if not profile_data:
        logger.error("Failed to retrieve profile data.")
        return

    nodes = split_profile_data(profile_data)
    index = create_vector_database(nodes)
    if not index:
        logger.error("Failed to create vector database.")
        return

    if not verify_embeddings(index):
        logger.warning("Some embeddings may be missing or invalid.")

    print("\nHere are 3 interesting facts about this person:")
    print(generate_initial_facts(index))
    chatbot_interface(index)


def chatbot_interface(index) -> None:
    print(
        "\nAsk more questions about this person. "
        "Type 'exit', 'quit', or 'bye' to quit."
    )
    while True:
        user_query = input("You: ")
        if user_query.lower() in {"exit", "quit", "bye"}:
            print("Bot: Goodbye!")
            break
        print("Bot is typing...", end="")
        sys.stdout.flush()
        time.sleep(0.3)
        print("\r", end="")
        response = answer_user_query(index, user_query)
        text = getattr(response, "response", None) or str(response)
        print(f"Bot: {str(text).strip()}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Icebreaker Bot — LinkedIn profile RAG")
    parser.add_argument("--url", type=str, help="LinkedIn profile URL")
    parser.add_argument("--api-key", type=str, help="ProxyCurl API key")
    parser.add_argument("--mock", action="store_true", help="Use mock LinkedIn JSON")
    parser.add_argument("--model", type=str, help="Override LLM model id")
    args = parser.parse_args()

    print(describe_llama_index_llm())
    print(f"Embeddings={config.EMBEDDING_MODEL}")

    if args.model:
        change_llm_model(args.model)

    linkedin_url = args.url or ""
    use_mock = args.mock or not linkedin_url
    if not args.url and not args.mock:
        entered = input("Enter LinkedIn profile URL (or press Enter to use mock data): ").strip()
        linkedin_url = entered
        use_mock = not linkedin_url

    api_key = args.api_key or config.PROXYCURL_API_KEY
    if not use_mock and not api_key:
        api_key = input("Enter ProxyCurl API key: ").strip()

    if use_mock and not linkedin_url:
        linkedin_url = config.DEFAULT_MOCK_URL

    process_linkedin(linkedin_url, api_key, mock=use_mock)


if __name__ == "__main__":
    main()
