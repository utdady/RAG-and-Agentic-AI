"""
DocChat — multi-agent RAG (Gradio).

Upload docs → hybrid BM25+Chroma → LangGraph relevance → research → verify.
Watsonx/Slate/Docling-course stack → shared.llm + MiniLM (+ Docling optional).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Dict, List

import gradio as gr

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shared.env_load import load_env

load_env(HERE)

from agents.workflow import AgentWorkflow
from config import constants
from document_processor.file_handler import DocumentProcessor
from retriever.builder import RetrieverBuilder
from shared.llm import describe_setup
from utils.logging import logger

print(describe_setup())


def _get_file_hashes(uploaded_files: List) -> frozenset:
    hashes = set()
    for file in uploaded_files:
        path = Path(getattr(file, "name", file))
        with open(path, "rb") as f:
            hashes.add(hashlib.sha256(f.read()).hexdigest())
    return frozenset(hashes)


def main():
    processor = DocumentProcessor()
    retriever_builder = RetrieverBuilder()
    workflow = AgentWorkflow()

    with gr.Blocks(title="DocChat") as demo:
        gr.Markdown("# DocChat")
        gr.Markdown(
            "Multi-agent RAG: **relevance → research → verification** "
            "(LangGraph). Upload `.pdf` / `.docx` / `.txt` / `.md`, then ask.  \n"
            f"`{describe_setup()}`"
        )
        session_state = gr.State({"file_hashes": frozenset(), "retriever": None})

        with gr.Row():
            with gr.Column():
                files = gr.Files(
                    label="Upload documents",
                    file_types=constants.ALLOWED_TYPES,
                )
                question = gr.Textbox(label="Question", lines=3)
                submit_btn = gr.Button("Submit", variant="primary")
            with gr.Column():
                answer_output = gr.Textbox(label="Answer", lines=12)
                verification_output = gr.Textbox(label="Verification report", lines=10)

        def process_question(question_text: str, uploaded_files: List, state: Dict):
            try:
                if not (question_text or "").strip():
                    raise ValueError("Question cannot be empty")
                if not uploaded_files:
                    raise ValueError("No documents uploaded")

                current_hashes = _get_file_hashes(uploaded_files)
                if state["retriever"] is None or current_hashes != state["file_hashes"]:
                    logger.info("Building retriever for new/changed docs…")
                    chunks = processor.process(uploaded_files)
                    if not chunks:
                        raise ValueError("No text chunks extracted from uploads")
                    retriever = retriever_builder.build_hybrid_retriever(chunks)
                    state = {
                        "file_hashes": current_hashes,
                        "retriever": retriever,
                    }

                result = workflow.full_pipeline(
                    question=question_text.strip(),
                    retriever=state["retriever"],
                )
                return result["draft_answer"], result["verification_report"], state
            except Exception as e:
                logger.error("Processing error: %s", e)
                return f"Error: {e}", "", state

        submit_btn.click(
            fn=process_question,
            inputs=[question, files, session_state],
            outputs=[answer_output, verification_output, session_state],
        )

    import os

    host = os.getenv("GRADIO_HOST", "127.0.0.1")
    port = int(os.getenv("GRADIO_PORT", "7867"))
    demo.launch(server_name=host, server_port=port, share=False)


if __name__ == "__main__":
    main()
