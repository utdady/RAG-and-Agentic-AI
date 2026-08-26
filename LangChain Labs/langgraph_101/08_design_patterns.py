"""08 — LangGraph design patterns: orchestrator–worker (Send) + evaluator–optimizer.

Course: OpenAI + litellm SSL off + pygraphviz.
Here: shared.llm; mermaid; educational demos only (not financial advice).
"""

from __future__ import annotations

import operator
from pprint import pprint
from typing import Annotated, List, Literal, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

from _bootstrap import banner
from shared.llm import get_llm_info

banner("08 Design patterns (orchestrator–worker + optimizer)")

llm, info = get_llm_info(temperature=0.5)
print(f"Using {info.provider}:{info.model}")
print("Disclaimer: investment demo is educational only — not financial advice.\n")


def _show(app, title: str) -> None:
    print(f"\n--- {title} (mermaid) ---")
    try:
        print(app.get_graph().draw_mermaid())
    except Exception as e:
        print(f"(mermaid unavailable: {e})")


# ---------------------------------------------------------------------------
# Pattern A: Orchestrator → chef workers (Send) → synthesizer
# ---------------------------------------------------------------------------


class Dish(BaseModel):
    name: str = Field(description="Name of the dish")
    ingredients: List[str] = Field(description="Ingredients for this dish")
    location: str = Field(description="Cuisine / cultural origin")


class Dishes(BaseModel):
    sections: List[Dish] = Field(description="One section per dish")


dish_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You generate a structured grocery/meal plan.\n"
            "Meals requested: {meals}\n"
            "For each meal return name, ingredients list, and cuisine origin.",
        )
    ]
)
planner_pipe = dish_prompt | llm.with_structured_output(Dishes)

chef_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a chef from {location}.\n"
            "Introduce yourself briefly and walk through preparing {name}.\n"
            "Include prep steps and cooking process.\n"
            "Ingredients: {ingredients}.",
        )
    ]
)
chef_pipe = chef_prompt | llm


class MealState(TypedDict, total=False):
    meals: str
    sections: List[Dish]
    completed_menu: Annotated[List[str], operator.add]
    final_meal_guide: str


class WorkerState(TypedDict, total=False):
    section: Dish
    completed_menu: Annotated[list, operator.add]


def orchestrator(state: MealState) -> dict:
    dish_descriptions = planner_pipe.invoke({"meals": state["meals"]})
    return {"sections": dish_descriptions.sections}


def assign_workers(state: MealState):
    return [Send("chef_worker", {"section": s}) for s in state["sections"]]


def chef_worker(state: WorkerState) -> dict:
    section = state["section"]
    meal_plan = chef_pipe.invoke(
        {
            "name": section.name,
            "location": section.location,
            "ingredients": section.ingredients,
        }
    )
    content = getattr(meal_plan, "content", str(meal_plan))
    return {"completed_menu": [content]}


def synthesizer(state: MealState) -> dict:
    completed = state.get("completed_menu") or []
    return {"final_meal_guide": "\n\n---\n\n".join(completed)}


def build_orchestrator_worker():
    g = StateGraph(MealState)
    g.add_node("orchestrator", orchestrator)
    g.add_node("chef_worker", chef_worker)
    g.add_node("synthesizer", synthesizer)
    g.add_edge(START, "orchestrator")
    g.add_conditional_edges("orchestrator", assign_workers, ["chef_worker"])
    g.add_edge("chef_worker", "synthesizer")
    g.add_edge("synthesizer", END)
    return g.compile()


# ---------------------------------------------------------------------------
# Pattern B: Evaluator–optimizer (investment plan loop)
# ---------------------------------------------------------------------------

grades = Literal[
    "ultra-conservative",
    "conservative",
    "moderate",
    "aggressive",
    "high risk",
]


class InvestState(TypedDict, total=False):
    investment_plan: str
    investor_profile: str
    target_grade: str
    feedback: str
    grade: str
    n: int


class Feedback(BaseModel):
    grade: grades = Field(description="Risk classification")
    feedback: str = Field(description="Reasoning for the grade")


grade_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Pick exactly one risk classification for this investor: "
            "ultra-conservative, conservative, moderate, aggressive, high risk. "
            "Return ONLY the grade label.",
        ),
        ("user", "Investor profile:\n\n{investor_profile}"),
    ]
)
grade_pipe = grade_prompt | llm

cathie_wood_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a bold, growth-oriented investment educator (lab persona). "
            "Write a concise paragraph investment plan for the profile. "
            "Educational only — not advice.",
        ),
        ("human", "Investor profile:\n\n{investor_profile}"),
    ]
)
cathie_wood_pipe = cathie_wood_prompt | llm

ray_dalio_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You revise investment plans based on evaluator feedback "
            "(lab persona). Adapt allocations to address the critique. "
            "Educational only — not advice.",
        ),
        (
            "human",
            "Profile:\n{investor_profile}\n\n"
            "Previous grade: {grade}\nFeedback: {feedback}\n\n"
            "Write a NEW plan addressing the feedback.",
        ),
    ]
)
ray_dalio_pipe = ray_dalio_prompt | llm

evaluator_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You evaluate investment plans for risk alignment (lab persona). "
            "Return structured grade + feedback. Grades: ultra-conservative, "
            "conservative, moderate, aggressive, high risk.",
        ),
        (
            "human",
            "Plan:\n{investment_plan}\n\nProfile:\n{investor_profile}\n\n"
            "Target risk level to match: {target_grade}",
        ),
    ]
)
buffett_evaluator_pipe = evaluator_prompt | llm.with_structured_output(Feedback)


def determine_target_grade(state: InvestState) -> dict:
    response = grade_pipe.invoke({"investor_profile": state["investor_profile"]})
    text = (getattr(response, "content", None) or str(response)).strip().lower()
    return {"target_grade": text}


def investment_plan_generator(state: InvestState) -> dict:
    if state.get("feedback"):
        response = ray_dalio_pipe.invoke(
            {
                "investor_profile": state["investor_profile"],
                "grade": state.get("grade", ""),
                "feedback": state["feedback"],
            }
        )
    else:
        response = cathie_wood_pipe.invoke(
            {"investor_profile": state["investor_profile"]}
        )
    return {"investment_plan": getattr(response, "content", str(response))}


def evaluate_plan(state: InvestState) -> dict:
    current_count = int(state.get("n") or 0) + 1
    evaluation = buffett_evaluator_pipe.invoke(
        {
            "investment_plan": state["investment_plan"],
            "investor_profile": state["investor_profile"],
            "target_grade": state["target_grade"],
        }
    )
    return {
        "grade": evaluation.grade,
        "feedback": evaluation.feedback,
        "n": current_count,
    }


def route_investment(state: InvestState, iteration_limit: int = 3) -> str:
    current = (state.get("grade") or "").strip().lower()
    target = (state.get("target_grade") or "").strip().lower()
    n = int(state.get("n") or 0)
    print(f"[route] grade={current!r} target={target!r} n={n}")
    if current == target or n > iteration_limit:
        return "Accepted"
    return "Rejected + Feedback"


def build_optimizer():
    g = StateGraph(InvestState)
    g.add_node("determine_target_grade", determine_target_grade)
    g.add_node("investment_plan_generator", investment_plan_generator)
    g.add_node("evaluate_plan", evaluate_plan)
    g.add_edge(START, "determine_target_grade")
    g.add_edge("determine_target_grade", "investment_plan_generator")
    g.add_edge("investment_plan_generator", "evaluate_plan")
    g.add_conditional_edges(
        "evaluate_plan",
        route_investment,
        {
            "Accepted": END,
            "Rejected + Feedback": "investment_plan_generator",
        },
    )
    return g.compile()


def pretty_print_final_state(state: dict) -> None:
    print("\nFinal Investment Plan Summary")
    print("=" * 40)
    print(f"\nProfile:\n{state.get('investor_profile')}")
    print(f"\nTarget: {state.get('target_grade')}")
    print(f"Final grade: {state.get('grade')}")
    print(f"Iterations: {state.get('n')}")
    print(f"\nFeedback:\n{state.get('feedback')}")
    plan = state.get("investment_plan") or ""
    print(f"\nPlan (preview):\n{plan[:800]}{'…' if len(plan) > 800 else ''}")


if __name__ == "__main__":
    print("\n===== A) Orchestrator–worker (meals) =====")
    ow = build_orchestrator_worker()
    _show(ow, "orchestrator-worker")
    meal_state = ow.invoke({"meals": "Steak and eggs, tacos, and chili"})
    guide = meal_state.get("final_meal_guide") or ""
    print("\nMeal guide preview:\n")
    pprint(guide[:1500] + ("…" if len(guide) > 1500 else ""))

    print("\n===== B) Evaluator–optimizer (investment) =====")
    opt = build_optimizer()
    _show(opt, "evaluator-optimizer")
    inv = opt.invoke(
        {
            "investor_profile": (
                "Age: 29\n"
                "Salary: $110,000\n"
                "Assets: $40,000\n"
                "Goal: Achieve financial independence by age 45\n"
                "Risk tolerance: High"
            ),
            "n": 0,
        }
    )
    pretty_print_final_state(inv)
