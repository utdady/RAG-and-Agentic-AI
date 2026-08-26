"""07 — LangGraph workflow patterns: chain, router, parallel fan-out, multi-router.

Course: OpenAI + pygraphviz. Here: shared.llm + mermaid text.
"""

from __future__ import annotations

from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from _bootstrap import banner
from shared.llm import get_llm_info

banner("07 Workflow patterns")

llm, info = get_llm_info(temperature=0.3)
print(f"Using {info.provider}:{info.model}")


def _show(app, title: str) -> None:
    print(f"\n--- {title} (mermaid) ---")
    try:
        print(app.get_graph().draw_mermaid())
    except Exception as e:
        print(f"(mermaid unavailable: {e})")


# ---------------------------------------------------------------------------
# 1) Sequential chain: job → resume summary → cover letter
# ---------------------------------------------------------------------------


class ChainState(TypedDict, total=False):
    job_description: str
    resume_summary: str
    cover_letter: str


def generate_resume_summary(state: ChainState) -> dict:
    prompt = f"""You're a resume assistant. Summarize key qualifications for this job
as if from a strong applicant's resume summary.

Job Description:
{state['job_description']}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"resume_summary": getattr(response, "content", str(response))}


def generate_cover_letter(state: ChainState) -> dict:
    prompt = f"""Write a professional cover letter using this resume summary and job.

Resume Summary:
{state['resume_summary']}

Job Description:
{state['job_description']}
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"cover_letter": getattr(response, "content", str(response))}


def build_chain_app():
    workflow = StateGraph(ChainState)
    workflow.add_node("generate_resume_summary", generate_resume_summary)
    workflow.add_node("generate_cover_letter", generate_cover_letter)
    workflow.set_entry_point("generate_resume_summary")
    workflow.add_edge("generate_resume_summary", "generate_cover_letter")
    workflow.add_edge("generate_cover_letter", END)
    return workflow.compile()


# ---------------------------------------------------------------------------
# 2) Router: summarize vs translate
# ---------------------------------------------------------------------------


class SimpleRouterState(TypedDict, total=False):
    user_input: str
    task_type: str
    output: str


class SimpleRouter(BaseModel):
    role: str = Field(
        ...,
        description="Return exactly 'summarize' or 'translate'.",
    )


def build_simple_router_app():
    llm_router = llm.bind_tools([SimpleRouter])

    def router_node(state: SimpleRouterState) -> dict:
        routing_prompt = f"""Classify the user request as summarize or translate.
User Input: "{state['user_input']}"
"""
        response = llm_router.invoke([HumanMessage(content=routing_prompt)])
        if getattr(response, "tool_calls", None):
            role = response.tool_calls[0]["args"].get("role", "summarize")
        else:
            text = (getattr(response, "content", "") or "").lower()
            role = "translate" if "translate" in text else "summarize"
        if role not in {"summarize", "translate"}:
            role = "summarize"
        return {"task_type": role}

    def route(state: SimpleRouterState) -> str:
        return state["task_type"]

    def summarize_node(state: SimpleRouterState) -> dict:
        response = llm.invoke(
            [
                HumanMessage(
                    content=f"Summarize:\n\n{state['user_input']}"
                )
            ]
        )
        return {
            "task_type": "summarize",
            "output": getattr(response, "content", str(response)),
        }

    def translate_node(state: SimpleRouterState) -> dict:
        response = llm.invoke(
            [
                HumanMessage(
                    content=f"Translate to French:\n\n{state['user_input']}"
                )
            ]
        )
        return {
            "task_type": "translate",
            "output": getattr(response, "content", str(response)),
        }

    workflow = StateGraph(SimpleRouterState)
    workflow.add_node("router", router_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("translate", translate_node)
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        route,
        {"summarize": "summarize", "translate": "translate"},
    )
    workflow.add_edge("summarize", END)
    workflow.add_edge("translate", END)
    return workflow.compile()


# ---------------------------------------------------------------------------
# 3) Parallel fan-out: FR / ES / JA → aggregator
# ---------------------------------------------------------------------------


class ParallelState(TypedDict, total=False):
    text: str
    french: str
    spanish: str
    japanese: str
    combined_output: str


def translate_french(state: ParallelState) -> dict:
    response = llm.invoke(
        [HumanMessage(content=f"Translate to French:\n\n{state['text']}")]
    )
    return {"french": getattr(response, "content", str(response)).strip()}


def translate_spanish(state: ParallelState) -> dict:
    response = llm.invoke(
        [HumanMessage(content=f"Translate to Spanish:\n\n{state['text']}")]
    )
    return {"spanish": getattr(response, "content", str(response)).strip()}


def translate_japanese(state: ParallelState) -> dict:
    response = llm.invoke(
        [HumanMessage(content=f"Translate to Japanese:\n\n{state['text']}")]
    )
    return {"japanese": getattr(response, "content", str(response)).strip()}


def aggregator(state: ParallelState) -> dict:
    combined = (
        f"Original Text: {state['text']}\n\n"
        f"French: {state.get('french')}\n\n"
        f"Spanish: {state.get('spanish')}\n\n"
        f"Japanese: {state.get('japanese')}\n"
    )
    return {"combined_output": combined}


def build_parallel_app():
    graph = StateGraph(ParallelState)
    graph.add_node("translate_french", translate_french)
    graph.add_node("translate_spanish", translate_spanish)
    graph.add_node("translate_japanese", translate_japanese)
    graph.add_node("aggregator", aggregator)
    graph.add_edge(START, "translate_french")
    graph.add_edge(START, "translate_spanish")
    graph.add_edge(START, "translate_japanese")
    graph.add_edge("translate_french", "aggregator")
    graph.add_edge("translate_spanish", "aggregator")
    graph.add_edge("translate_japanese", "aggregator")
    graph.add_edge("aggregator", END)
    return graph.compile()


# ---------------------------------------------------------------------------
# 4) Exercise: multi-service router
# ---------------------------------------------------------------------------


class ServiceRouterState(TypedDict, total=False):
    user_input: str
    task_type: str
    output: str


class ServiceRouter(BaseModel):
    role: str = Field(
        ...,
        description=(
            "Classify as exactly one of: ride_hailing_call, restaurant_order, "
            "groceries, default_handler"
        ),
    )


def build_service_router_app():
    llm_router = llm.bind_tools([ServiceRouter])

    def router_node(state: ServiceRouterState) -> dict:
        response = llm_router.invoke(
            [HumanMessage(content=state["user_input"])]
        )
        if getattr(response, "tool_calls", None):
            role = response.tool_calls[0]["args"].get("role", "default_handler")
        else:
            role = "default_handler"
        allowed = {
            "ride_hailing_call",
            "restaurant_order",
            "groceries",
            "default_handler",
        }
        if role not in allowed:
            role = "default_handler"
        return {"task_type": role}

    def route(state: ServiceRouterState) -> str:
        return state["task_type"]

    def ride_hailing_node(state: ServiceRouterState) -> dict:
        prompt = f"""Extract ride details (pickup, dropoff, preferences) from:
"{state['user_input']}"
Provide a clear summary."""
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            "task_type": "ride_hailing_call",
            "output": getattr(response, "content", str(response)).strip(),
        }

    def restaurant_order_node(state: ServiceRouterState) -> dict:
        prompt = f"""Organize this restaurant order (items, qty, mods, delivery/pickup):
"{state['user_input']}"
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            "task_type": "restaurant_order",
            "output": getattr(response, "content", str(response)).strip(),
        }

    def groceries_node(state: ServiceRouterState) -> dict:
        prompt = f"""Organize a grocery delivery shopping list and driver notes from:
"{state['user_input']}"
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            "task_type": "groceries",
            "output": getattr(response, "content", str(response)).strip(),
        }

    def default_handler_node(state: ServiceRouterState) -> dict:
        prompt = f"""The request wasn't classified. Offer help for ride hailing,
restaurant orders, or groceries. User said: "{state['user_input']}"
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            "task_type": "default_handler",
            "output": getattr(response, "content", str(response)).strip(),
        }

    workflow = StateGraph(ServiceRouterState)
    workflow.add_node("router", router_node)
    workflow.add_node("ride_hailing_call", ride_hailing_node)
    workflow.add_node("restaurant_order", restaurant_order_node)
    workflow.add_node("groceries", groceries_node)
    workflow.add_node("default_handler", default_handler_node)
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        route,
        {
            "groceries": "groceries",
            "restaurant_order": "restaurant_order",
            "ride_hailing_call": "ride_hailing_call",
            "default_handler": "default_handler",
        },
    )
    for name in (
        "ride_hailing_call",
        "restaurant_order",
        "groceries",
        "default_handler",
    ):
        workflow.add_edge(name, END)
    return workflow.compile()


if __name__ == "__main__":
    print("\n===== 1) Sequential chain =====")
    chain = build_chain_app()
    _show(chain, "chain")
    job = {
        "job_description": (
            "We are looking for a data scientist with experience in machine "
            "learning, NLP, and Python. Prior work with large datasets and "
            "experience deploying models into production is required."
        )
    }
    r = chain.invoke(job)
    print("\nResume summary:\n", r.get("resume_summary", "")[:500], "…\n")
    print("Cover letter (preview):\n", (r.get("cover_letter") or "")[:400], "…\n")

    print("\n===== 2) Simple router =====")
    simple = build_simple_router_app()
    _show(simple, "simple router")
    for q in (
        "Can you translate this sentence: I love programming?",
        "Can you summarize this sentence: I love programming so much it is the best thing ever.",
    ):
        out = simple.invoke({"user_input": q})
        print(f"\nQ: {q}\ntask={out.get('task_type')}\n{out.get('output')}\n")

    print("\n===== 3) Parallel translations =====")
    parallel = build_parallel_app()
    _show(parallel, "parallel")
    pr = parallel.invoke(
        {"text": "Good morning! I hope you have a wonderful day."}
    )
    print(pr.get("combined_output"))

    print("\n===== 4) Multi-service router =====")
    services = build_service_router_app()
    _show(services, "service router")
    tests = [
        "I need a ride from downtown to the airport at 3pm",
        "I want to order 2 large pepperoni pizzas for delivery",
        "I need milk, bread, eggs, and vegetables for the week",
        "What's the weather like today?",
    ]
    for q in tests:
        out = services.invoke({"user_input": q})
        print(f"\nQ: {q}\ntask={out.get('task_type')}\n{out.get('output')}\n---")
