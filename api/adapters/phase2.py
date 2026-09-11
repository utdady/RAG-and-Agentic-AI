from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from api.adapters.common import finish_text, require_groq
from api.bootstrap import add_app, prepare_app_import, prepare_demo_import
from api.events import context, task, thinking

_ice_sid: str | None = None
_food_items: list[dict[str, Any]] | None = None


def run_connoisseur(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    question = (payload.get("message") or "").strip()
    prepare_demo_import("Connoisseur Companion", chdir=True)
    import json

    from agents.workflow import (  # noqa: WPS433
        AGENT_PROMPTS,
        _analyze,
        _call_llm,
        _parse_json,
        format_recommendations,
        generate_profile,
        retrieve_candidates,
    )

    yield thinking("Building dining profile")
    yield task("profile", "Profile generator", "running")
    profile = generate_profile(question)
    yield task("profile", "Profile generator", "completed")

    yield thinking("Searching dining knowledge")
    yield task("retrieve", "Knowledge retrieval", "running")
    candidates = retrieve_candidates(profile)
    yield task("retrieve", "Knowledge retrieval", "completed")

    analysis_payload = {
        "profile": profile,
        "retrieved_restaurants": candidates.get("restaurants", [])[:10],
        "retrieved_recipes": candidates.get("recipes", [])[:10],
    }

    yield thinking("Analyzing food trends")
    yield task("trends", "Trend analyst", "running")
    trends = _analyze("trends", analysis_payload)
    yield task("trends", "Trend analyst", "completed")

    yield thinking("Matching cuisine styles")
    yield task("styles", "Style expert", "running")
    styles = _analyze("styles", analysis_payload)
    yield task("styles", "Style expert", "completed")

    yield thinking("Checking nutrition fit")
    yield task("nutrition", "Nutrition expert", "running")
    nutrition = _analyze("nutrition", analysis_payload)
    yield task("nutrition", "Nutrition expert", "completed")

    yield thinking("Synthesizing recommendations")
    yield task("synthesize", "Recommendations", "running")
    synthesis_payload = {
        **analysis_payload,
        "trends": trends,
        "styles": styles,
        "nutrition": nutrition,
    }
    recommendations = _parse_json(
        _call_llm(AGENT_PROMPTS["recommend"], json.dumps(synthesis_payload, indent=2))
    )
    yield task("synthesize", "Recommendations", "completed")

    result = {
        "profile": profile,
        "candidates": candidates,
        "analysis": {"trends": trends, "styles": styles, "nutrition": nutrition},
        "recommendations": recommendations,
    }
    hits = result.get("candidates") or {}
    docs = hits.get("documents") or hits.get("results") or []
    if isinstance(docs, list) and docs:
        snippet = str(docs[0])[:280]
        yield context("Retrieved dining knowledge", snippet, "connoisseur RAG")
    text = format_recommendations(result)
    yield from finish_text(text)


def run_docchat(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    question = (payload.get("message") or "").strip()
    files: list[str] = payload.get("file_paths") or []
    if not files:
        yield from finish_text("Upload one or more documents first.")
        return
    if not question:
        yield from finish_text(
            "Ask a question about your documents (upload alone is not enough)."
        )
        return

    from api.errors import humanize_exception
    from api.events import done, error
    from langchain_community.retrievers import BM25Retriever

    prepare_demo_import("DocChat", chdir=True)
    import importlib

    try:
        workflow_mod = importlib.import_module("agents.workflow")
        AgentWorkflow = workflow_mod.AgentWorkflow
        DocumentProcessor = importlib.import_module(
            "document_processor.file_handler"
        ).DocumentProcessor
    except Exception as exc:  # noqa: BLE001
        friendly = humanize_exception(exc)
        yield error(friendly.message, title=friendly.title)
        yield done()
        return

    yield thinking("Processing uploaded documents")
    yield task("index", "Document indexer", "running")
    try:
        processor = DocumentProcessor()
        chunks = processor.process(files)
        if not chunks:
            yield task("index", "Document indexer", "failed")
            yield from finish_text(
                "Couldn't extract text from the upload. Try a text-based PDF, DOCX, TXT, or MD file."
            )
            return
        # BM25-only on the hub: MiniLM + Chroma OOMs free/small Render instances.
        retriever = BM25Retriever.from_documents(chunks)
        retriever.k = 6
        yield task("index", "Document indexer", "completed")
    except Exception as exc:  # noqa: BLE001
        yield task("index", "Document indexer", "failed")
        friendly = humanize_exception(exc)
        yield error(friendly.message, title=friendly.title)
        yield done()
        return

    try:
        yield thinking("Building research workflow")
        workflow = AgentWorkflow()
        documents = retriever.invoke(question)

        state = {
            "question": question,
            "documents": documents,
            "draft_answer": "",
            "verification_report": "",
            "is_relevant": False,
            "retriever": retriever,
            "research_loops": 0,
        }

        yield thinking("Checking question relevance")
        yield task("relevance", "Relevance check", "running")
        state.update(workflow._check_relevance_step(state))
        yield task("relevance", "Relevance check", "completed")

        if not state["is_relevant"]:
            answer = state.get("draft_answer") or ""
            report = state.get("verification_report") or ""
        else:
            while True:
                yield thinking("Researching documents")
                yield task("research", "Research agent", "running")
                state.update(workflow._research_step(state))
                yield task("research", "Research agent", "completed")

                yield thinking("Verifying answer")
                yield task("verify", "Verification", "running")
                state.update(workflow._verification_step(state))
                yield task("verify", "Verification", "completed")

                if workflow._decide_next_step(state) != "re_research":
                    break
                yield thinking("Refining research")

            answer = state.get("draft_answer") or ""
            report = state.get("verification_report") or ""
    except Exception as exc:  # noqa: BLE001
        friendly = humanize_exception(exc)
        yield error(friendly.message, title=friendly.title)
        yield done()
        return

    extras = []
    if report:
        extras.append(
            {
                "type": "context",
                "title": "Verification report",
                "snippet": report[:800],
                "source": "DocChat verifier",
            }
        )
    yield from finish_text(
        answer or "I couldn't produce an answer from these documents. Try a more specific question.",
        extras,
    )


def run_food_search(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    query = (payload.get("message") or "").strip()
    if not query:
        yield from finish_text("Describe what you want to eat (cuisine, calories, vibe).")
        return

    from api.errors import humanize_exception
    from api.events import done, error

    yield thinking("Loading food catalog")
    add_app("Food Search RAG")
    try:
        from download_data import main as download_assets  # noqa: WPS433
        from rag_chat import generate_llm_rag_response  # noqa: WPS433
        from shared_food import load_food_data, perform_keyword_search  # noqa: WPS433
    except Exception as exc:  # noqa: BLE001
        friendly = humanize_exception(exc)
        yield error(friendly.message, title=friendly.title)
        yield done()
        return

    global _food_items
    try:
        download_assets()
        if _food_items is None:
            _food_items = load_food_data()
        if not _food_items:
            yield from finish_text("Food catalog failed to load. Try again in a moment.")
            return

        yield thinking("Matching dishes to your request")
        # Keyword search only — Chroma + MiniLM OOMs small Render instances.
        hits = perform_keyword_search(_food_items, query, n_results=5)
        if hits:
            yield context(
                hits[0].get("food_name", "Match"),
                str(hits[0].get("food_description", ""))[:400],
                hits[0].get("cuisine_type", "food"),
            )
        yield thinking("Writing recommendations")
        text = generate_llm_rag_response(query, hits)
        yield from finish_text(text)
    except Exception as exc:  # noqa: BLE001
        friendly = humanize_exception(exc)
        yield error(friendly.message, title=friendly.title)
        yield done()


def run_icebreaker(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    question = (payload.get("message") or "").strip()
    yield thinking("Loading mock LinkedIn profile")
    prepare_app_import("Icebreaker Bot", chdir=True)
    global _ice_sid
    from app import active_indices, chat_with_profile, process_profile  # noqa: WPS433
    from modules.llm_interface import available_models  # noqa: WPS433

    models = available_models()
    model = models[0] if models else ""
    if not _ice_sid or _ice_sid not in active_indices:
        facts, new_id = process_profile("", None, True, model)
        if not new_id:
            yield from finish_text(str(facts))
            return
        _ice_sid = new_id
        yield context("Profile facts", str(facts)[:600], "mock LinkedIn JSON")
        if not question:
            yield from finish_text(str(facts))
            return
    history = chat_with_profile(_ice_sid, question, [])
    answer = history[-1][1] if history else ""
    yield from finish_text(str(answer))
