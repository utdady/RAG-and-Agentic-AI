"""05 — Reflection + Tavily search (structured AnswerQuestion / ReviseAnswer).

Course: OpenAI + Tavily MessageGraph (respond → tools → revisor loop).
Here: shared.llm (prefer Groq for tool calling) + TAVILY_API_KEY from .env.

Not medical advice — course persona is opinionated nutrition rhetoric for the lab.
"""

from __future__ import annotations

import json
import os
from typing import List

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, MessageGraph
from pydantic import BaseModel, Field

from _bootstrap import banner
from shared.llm import get_llm_info, resolve_provider

banner("05 Reflection + external search (Tavily)")

if not os.getenv("TAVILY_API_KEY", "").strip():
    raise SystemExit(
        "Set TAVILY_API_KEY in repo-root .env (https://tavily.com). "
        "Do not hardcode keys in source."
    )

if resolve_provider() == "ollama":
    print(
        "Warning: structured tool-calling is more reliable on Groq; "
        "set GROQ_API_KEY if this run fails."
    )

llm, info = get_llm_info(temperature=0.3)
print(f"Using {info.provider}:{info.model}")

tavily_tool = TavilySearchResults(max_results=3)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a nutrition education assistant for a LangGraph lab demo
            (inspired by animal-based / low-carb talking points from the course notebook).
            Stay evidence-oriented where possible. This is NOT medical advice.

            Your response must follow these steps:
            1. {first_instruction}
            2. Give a clear mechanistic/practical rationale for breakfast choices.
            3. Note uncertainties and individual variability.
            4. Reflect and critique your answer (missing / superfluous).
            5. After the reflection, list 1-3 search queries separately for research
               (biomarkers, RCTs, antinutrients, glycemic impact, etc.).
            """,
        ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Answer the user's question above using the required tool/schema format.",
        ),
    ]
)

first_responder_prompt = prompt_template.partial(
    first_instruction="Provide a detailed ~250 word answer"
)

revise_instructions = """Revise your previous answer using the new search results.
- Incorporate the previous critique; prefer mechanistic clarity and individual variability.
- Include numerical citations where URLs from tools support claims.
- Distinguish correlation vs causation; note research limits.
- Add a "References" section at the bottom (does not count toward word limit):
  [1] https://...
- Keep the main answer under ~250 words. NOT medical advice.
"""


class Reflection(BaseModel):
    missing: str = Field(description="What information is missing")
    superfluous: str = Field(description="What information is unnecessary")


class AnswerQuestion(BaseModel):
    """Initial structured answer with self-critique and follow-up searches."""

    answer: str = Field(description="Main response to the question")
    reflection: Reflection = Field(description="Self-critique of the answer")
    search_queries: List[str] = Field(description="Queries for additional research")


class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question."""

    references: List[str] = Field(
        description="Citations motivating your updated answer."
    )


initial_chain = first_responder_prompt | llm.bind_tools(tools=[AnswerQuestion])
revisor_prompt = prompt_template.partial(first_instruction=revise_instructions)
revisor_chain = revisor_prompt | llm.bind_tools(tools=[ReviseAnswer])

MAX_ITERATIONS = int(os.getenv("REFLECT_SEARCH_MAX_ITERS", "2"))


def execute_tools(state: List[BaseMessage]) -> List[BaseMessage]:
    last_ai = state[-1]
    tool_messages: List[ToolMessage] = []
    for tool_call in getattr(last_ai, "tool_calls", None) or []:
        if tool_call["name"] not in {"AnswerQuestion", "ReviseAnswer"}:
            continue
        call_id = tool_call["id"]
        search_queries = tool_call["args"].get("search_queries") or []
        query_results: dict = {}
        for query in search_queries:
            try:
                query_results[query] = tavily_tool.invoke(query)
            except Exception as e:
                query_results[query] = {"error": str(e)}
        tool_messages.append(
            ToolMessage(content=json.dumps(query_results), tool_call_id=call_id)
        )
    return tool_messages


def event_loop(state: List[BaseMessage]) -> str:
    count = sum(isinstance(item, ToolMessage) for item in state)
    if count >= MAX_ITERATIONS:
        return END
    return "execute_tools"


def build_app():
    graph = MessageGraph()
    graph.add_node("respond", initial_chain)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("revisor", revisor_chain)
    graph.set_entry_point("respond")
    graph.add_edge("respond", "execute_tools")
    graph.add_edge("execute_tools", "revisor")
    graph.add_conditional_edges("revisor", event_loop)
    return graph.compile()


DEMO = (
    "I'm pre-diabetic and need to lower my blood sugar, and I have heart issues. "
    "What breakfast foods should I eat and avoid?"
)


def _print_answers(responses: list) -> None:
    answers: list[str] = []
    for msg in reversed(responses):
        for tool_call in getattr(msg, "tool_calls", None) or []:
            ans = (tool_call.get("args") or {}).get("answer")
            if ans:
                answers.append(ans)
    for i, ans in enumerate(answers):
        label = "Final Revised Answer" if i == 0 else f"Intermediate Step {len(answers) - i}"
        print(f"\n===== {label} =====\n{ans}\n")


if __name__ == "__main__":
    print(
        "Disclaimer: educational LangGraph demo only — not medical or dietary advice.\n"
        f"MAX_ITERATIONS={MAX_ITERATIONS} (set REFLECT_SEARCH_MAX_ITERS to change; course used 4)."
    )
    app = build_app()
    responses = app.invoke(HumanMessage(content=DEMO))
    if not isinstance(responses, list):
        responses = list(responses)

    print("\n--- message types ---")
    for i, msg in enumerate(responses):
        print(f"[{i}] {type(msg).__name__}")

    _print_answers(responses)
