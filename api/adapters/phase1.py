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
    if not question:
        yield from finish_text("Ask a question about the Chinook music store database.")
        return
    yield thinking("Loading Chinook SQLite")
    add_app("Natural Language SQL Agent")
    from download_data import main as download_chinook  # noqa: WPS433

    download_chinook()
    from agent import run_query  # noqa: WPS433

    yield thinking("Translating your question to SQL")
    yield tool("sql_agent", "running")
    # Heartbeat while the blocking LangChain invoke runs so proxies/browsers
    # don't close the SSE stream before tokens arrive.
    import queue
    import threading

    result_q: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=1)

    def _work() -> None:
        try:
            result_q.put(("ok", run_query(question)))
        except Exception as exc:  # noqa: BLE001
            result_q.put(("err", exc))

    worker = threading.Thread(target=_work, daemon=True)
    worker.start()
    waited = 0
    while worker.is_alive():
        worker.join(timeout=6.0)
        if worker.is_alive():
            waited += 6
            yield thinking(f"Still writing SQL and querying Chinook… ({waited}s)")

    kind, payload_or_exc = result_q.get()
    if kind == "err":
        yield tool("sql_agent", "failed")
        yield from finish_text(
            f"The SQL agent hit an error: {payload_or_exc}\n\n"
            "Try a simpler question, or retry in a moment."
        )
        return
    answer = payload_or_exc
    yield tool("sql_agent", "done")
    yield from finish_text(str(answer or "").strip() or "No answer returned. Try rephrasing the question.")


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
    url = (payload.get("url") or "").strip()
    message = (payload.get("message") or "").strip()
    question = (payload.get("question") or "").strip()
    # Hub sends the URL in `url` and optional follow-up in `message`.
    if not url and message.startswith(("http://", "https://")):
        url, message = message, ""
    if not question and message and not message.startswith(("http://", "https://")):
        question = message
    if not url:
        yield from finish_text("Paste a YouTube URL first.")
        return

    yield thinking("Loading YouTube demo")
    prepare_app_import("YouTube Summarizer")
    from app import answer_question, summarize_video  # noqa: WPS433

    from api.errors import humanize_exception
    from api.events import done, error

    try:
        if question:
            yield thinking("Fetching transcript + answering")
            text = answer_question(url, question)
        else:
            yield thinking("Fetching transcript + summarizing")
            text = summarize_video(url)
    except Exception as exc:  # noqa: BLE001
        friendly = humanize_exception(exc)
        yield error(friendly.message, title=friendly.title)
        yield done()
        return
    yield from finish_text(text)
