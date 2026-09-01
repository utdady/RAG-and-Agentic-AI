from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from api.adapters.common import finish_text, require_groq
from api.bootstrap import add_app, prepare_app_import
from api.events import context, thinking, tool


def run_pdf_qa(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    path = payload.get("file_path")
    question = (payload.get("message") or "").strip()
    if not path:
        yield from finish_text("Upload a PDF first.")
        return
    yield thinking("Indexing PDF with MiniLM + Chroma")
    prepare_app_import("PDF QA Bot")
    from app import retriever_qa  # noqa: WPS433

    answer = retriever_qa(path, question)
    yield context("Retrieved chunks", "Answer grounded in the uploaded PDF.", path)
    yield from finish_text(answer)


def run_sql_agent(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    question = (payload.get("message") or "").strip()
    yield thinking("Loading Chinook SQLite")
    add_app("Natural Language SQL Agent")
    from download_data import main as download_chinook  # noqa: WPS433

    download_chinook()
    from agent import run_query  # noqa: WPS433

    yield tool("sql_agent", "running")
    answer = run_query(question)
    yield tool("sql_agent", "done")
    yield from finish_text(answer)


def run_math_assistant(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    question = (payload.get("message") or "").strip()
    yield thinking("ReAct math agent")
    add_app("AI Math Assistant")
    from agent import run_query  # noqa: WPS433

    yield tool("wikipedia / calculator", "running")
    answer, _ = run_query(question)
    yield tool("wikipedia / calculator", "done")
    yield from finish_text(answer)


def run_youtube(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    url = (payload.get("url") or payload.get("message") or "").strip()
    question = (payload.get("question") or "").strip()
    yield thinking("Fetching transcript")
    prepare_app_import("YouTube Summarizer")
    from app import answer_question, summarize_video  # noqa: WPS433

    if question:
        yield thinking("Answering from transcript RAG")
        text = answer_question(url, question)
    else:
        yield thinking("Summarizing transcript")
        text = summarize_video(url)
    yield from finish_text(text)
