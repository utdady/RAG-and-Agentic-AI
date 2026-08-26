"""02 — QA StateGraph: validate → context → LLM answer.

Watsonx ChatWatsonx → shared.llm (Groq/Ollama).
"""

from __future__ import annotations

from typing import Optional, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from _bootstrap import banner
from shared.llm import get_llm_info

banner("02 QA graph")

llm, info = get_llm_info(temperature=0)
print(f"Using {info.provider}:{info.model}")


class QAState(TypedDict, total=False):
    question: Optional[str]
    context: Optional[str]
    answer: Optional[str]
    valid: Optional[bool]
    error: Optional[str]


def input_validation_node(state: QAState) -> dict:
    question = (state.get("question") or "").strip()
    if not question:
        return {"valid": False, "error": "Question cannot be empty.", "answer": None}
    return {"valid": True, "error": None, "question": question}


def context_provider_node(state: QAState) -> dict:
    if not state.get("valid", True):
        return {"context": None}
    question = (state.get("question") or "").lower()
    if "langgraph" in question or "guided project" in question:
        return {
            "context": (
                "This guided project is about using LangGraph, a Python library "
                "to design state-based workflows. LangGraph simplifies building "
                "complex applications by connecting modular nodes with conditional edges."
            )
        }
    return {"context": None}


def llm_qa_node(state: QAState) -> dict:
    if state.get("valid") is False:
        return {"answer": state.get("error") or "Invalid input."}
    question = state.get("question") or ""
    context = state.get("context")
    if not context:
        return {"answer": "I don't have enough context to answer your question."}
    prompt = (
        f"Context: {context}\nQuestion: {question}\n"
        "Answer the question based on the provided context."
    )
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = getattr(response, "content", None) or str(response)
        return {"answer": str(content).strip()}
    except Exception as e:
        return {"answer": f"An error occurred: {e}"}


def build_app():
    qa_workflow = StateGraph(QAState)
    qa_workflow.add_node("InputNode", input_validation_node)
    qa_workflow.add_node("ContextNode", context_provider_node)
    qa_workflow.add_node("QANode", llm_qa_node)
    qa_workflow.set_entry_point("InputNode")
    qa_workflow.add_edge("InputNode", "ContextNode")
    qa_workflow.add_edge("ContextNode", "QANode")
    qa_workflow.add_edge("QANode", END)
    return qa_workflow.compile()


if __name__ == "__main__":
    qa_app = build_app()
    for q in (
        "What is the weather today?",
        "What is LangGraph?",
        "What is the best guided project?",
        "",
    ):
        print(f"\nQ: {q!r}")
        print(qa_app.invoke({"question": q}))
