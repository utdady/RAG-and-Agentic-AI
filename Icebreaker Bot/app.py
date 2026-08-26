"""Gradio web UI for the LinkedIn Icebreaker Bot."""

from __future__ import annotations

import logging
import sys
import uuid
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

load_dotenv(HERE / ".env")
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "Meeting Assistant" / ".env")

import config
from modules.data_extraction import extract_linkedin_profile
from modules.data_processing import (
    create_vector_database,
    split_profile_data,
    verify_embeddings,
)
from modules.llm_interface import available_models, change_llm_model
from modules.query_engine import answer_user_query, generate_initial_facts
from shared.llama_index_llm import describe_llama_index_llm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)
logger = logging.getLogger(__name__)

active_indices: dict[str, object] = {}


def process_profile(linkedin_url, api_key, use_mock, selected_model):
    try:
        change_llm_model(selected_model)
        if use_mock and not linkedin_url:
            linkedin_url = config.DEFAULT_MOCK_URL

        profile_data = extract_linkedin_profile(
            linkedin_url or config.DEFAULT_MOCK_URL,
            api_key if not use_mock else None,
            mock=bool(use_mock),
        )
        if not profile_data:
            return "Failed to retrieve profile data. Check the URL, API key, or use mock mode.", None

        nodes = split_profile_data(profile_data)
        if not nodes:
            return "Failed to process profile data into nodes.", None

        index = create_vector_database(nodes)
        if not index:
            return "Failed to create vector database.", None

        verify_embeddings(index)
        facts = generate_initial_facts(index)
        session_id = str(uuid.uuid4())
        active_indices[session_id] = index
        return (
            f"Profile processed successfully!\n\n"
            f"Here are 3 interesting facts about this person:\n\n{facts}",
            session_id,
        )
    except Exception as e:
        logger.error("Error in process_profile: %s", e)
        return f"Error: {e}", None


def chat_with_profile(session_id, user_query, chat_history):
    history = chat_history or []
    if not session_id:
        return history + [[user_query, "No profile loaded. Process a LinkedIn profile first."]]
    if session_id not in active_indices:
        return history + [[user_query, "Session expired. Process the profile again."]]
    if not (user_query or "").strip():
        return history
    try:
        response = answer_user_query(active_indices[session_id], user_query)
        text = getattr(response, "response", None) or str(response)
        return history + [[user_query, str(text)]]
    except Exception as e:
        logger.error("Error in chat_with_profile: %s", e)
        return history + [[user_query, f"Error: {e}"]]


def create_gradio_interface():
    models = available_models()
    with gr.Blocks(title="LinkedIn Icebreaker Bot") as demo:
        gr.Markdown("# LinkedIn Icebreaker Bot")
        gr.Markdown(
            f"Generate icebreakers and chat about a LinkedIn profile "
            f"({describe_llama_index_llm()}; embeddings={config.EMBEDDING_MODEL}). "
            "Default: mock profile JSON (no ProxyCurl key needed)."
        )
        session_id = gr.State(None)

        with gr.Tab("Process LinkedIn Profile"):
            with gr.Row():
                with gr.Column():
                    linkedin_url = gr.Textbox(
                        label="LinkedIn Profile URL",
                        placeholder="https://www.linkedin.com/in/username/",
                    )
                    api_key = gr.Textbox(
                        label="ProxyCurl API Key (only if not using mock)",
                        type="password",
                        value=config.PROXYCURL_API_KEY,
                    )
                    use_mock = gr.Checkbox(label="Use Mock Data", value=True)
                    model_dropdown = gr.Dropdown(
                        choices=models,
                        label="LLM Model",
                        value=models[0],
                    )
                    process_btn = gr.Button("Process Profile")
                with gr.Column():
                    result_text = gr.Textbox(label="Initial Facts", lines=12)

            process_btn.click(
                fn=process_profile,
                inputs=[linkedin_url, api_key, use_mock, model_dropdown],
                outputs=[result_text, session_id],
            )

        with gr.Tab("Chat"):
            gr.Markdown("Chat with the processed LinkedIn profile")
            chatbot = gr.Chatbot(height=500)
            chat_input = gr.Textbox(
                label="Ask a question about the profile",
                placeholder="What is this person's current job title?",
            )
            chat_btn = gr.Button("Send")

            chat_btn.click(
                fn=chat_with_profile,
                inputs=[session_id, chat_input, chatbot],
                outputs=[chatbot],
            )
            chat_input.submit(
                fn=chat_with_profile,
                inputs=[session_id, chat_input, chatbot],
                outputs=[chatbot],
            )

    return demo


if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(server_name="127.0.0.1", server_port=7862, share=False)
