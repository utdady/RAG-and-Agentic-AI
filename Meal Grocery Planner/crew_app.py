"""Build the meal / grocery CrewAI crew."""

from __future__ import annotations

import os
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

from llm_config import get_crew_llm
from schemas import GroceryShoppingPlan, MealPlan

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE / "outputs"


def build_crew(*, include_nutrition: bool = True) -> Crew:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    llm = get_crew_llm()

    # Hub demos often omit Serper; agents then plan from model knowledge only.
    search_tools: list = []
    if os.getenv("SERPER_API_KEY", "").strip():
        search_tools = [SerperDevTool()]

    research_hint = (
        "Search the web for current recipes and prices."
        if search_tools
        else (
            "Web search is unavailable — use solid culinary knowledge to invent "
            "a realistic recipe, ingredients, and approximate prices."
        )
    )

    meal_planner = Agent(
        role="Meal Planner & Recipe Researcher",
        goal="Search for optimal recipes and create detailed meal plans",
        backstory=(
            "A skilled meal planner who researches recipes online, considering "
            "dietary needs, cooking skill, and budget."
        ),
        tools=search_tools,
        llm=llm,
        verbose=True,
    )

    shopping_organizer = Agent(
        role="Shopping Organizer",
        goal="Organize grocery lists by store sections efficiently",
        backstory=(
            "An experienced shopper who organizes lists for quick store trips "
            "and respects dietary restrictions."
        ),
        tools=[],
        llm=llm,
        verbose=True,
    )

    budget_advisor = Agent(
        role="Budget Advisor",
        goal="Provide cost estimates and money-saving tips",
        backstory=(
            "A budget-conscious shopper who helps families save on groceries "
            "while respecting dietary needs."
        ),
        tools=search_tools,
        llm=llm,
        verbose=True,
    )

    meal_planning_task = Task(
        description=(
            f"{research_hint} Create the best '{{meal_name}}' recipe for "
            "{servings} people within a {budget} budget. Consider dietary "
            "restrictions: {dietary_restrictions} and cooking skill level: "
            "{cooking_skill}. Provide complete ingredient lists with quantities."
        ),
        expected_output=(
            "A detailed meal plan with researched ingredients, quantities, "
            "and cooking instructions appropriate for the skill level."
        ),
        agent=meal_planner,
        output_pydantic=MealPlan,
        output_file=str(OUTPUTS / "meals.json"),
    )

    shopping_task = Task(
        description=(
            "Organize the ingredients from the '{meal_name}' meal plan into a "
            "grocery shopping list. Group items by store sections and estimate "
            "quantities for {servings} people. Consider dietary restrictions: "
            "{dietary_restrictions} and cooking skill: {cooking_skill}. "
            "Stay within budget: {budget}."
        ),
        expected_output=(
            "An organized shopping list grouped by store sections with "
            "quantities and prices."
        ),
        agent=shopping_organizer,
        context=[meal_planning_task],
        output_pydantic=GroceryShoppingPlan,
        output_file=str(OUTPUTS / "shopping_list.json"),
    )

    budget_task = Task(
        description=(
            "Analyze the shopping plan for '{meal_name}' serving {servings} "
            "people. Ensure total cost stays within {budget}. Consider dietary "
            "restrictions: {dietary_restrictions}. Provide practical "
            "money-saving tips and alternative ingredients if needed."
        ),
        expected_output=(
            "A complete shopping guide with detailed prices, budget analysis, "
            "and money-saving tips."
        ),
        agent=budget_advisor,
        context=[meal_planning_task, shopping_task],
        output_file=str(OUTPUTS / "shopping_guide.md"),
    )

    # Leftovers via course YAML CrewBase helper
    from leftover import LeftoversCrew

    leftovers_cb = LeftoversCrew(llm=llm)
    leftover_manager = leftovers_cb.leftover_manager()
    leftover_task = leftovers_cb.leftover_task()
    # Ensure leftover task sees prior shopping context when supported
    try:
        leftover_task.context = [meal_planning_task, shopping_task, budget_task]
    except Exception:
        pass

    summary_agent = Agent(
        role="Report Compiler",
        goal="Compile comprehensive meal planning reports from all team outputs",
        backstory=(
            "A skilled coordinator who organizes specialist outputs into one "
            "easy-to-follow guide."
        ),
        tools=[],
        llm=llm,
        verbose=True,
    )

    agents = [
        meal_planner,
        shopping_organizer,
        budget_advisor,
        leftover_manager,
        summary_agent,
    ]
    prior_tasks = [
        meal_planning_task,
        shopping_task,
        budget_task,
        leftover_task,
    ]

    if include_nutrition:
        nutrition_analyst = Agent(
            role="Nutrition Analyst & Health Advisor",
            goal="Analyze meal nutritional content and provide healthy recommendations",
            backstory=(
                "A nutrition-focused advisor who estimates calories and macros "
                "and suggests improvements within budget. Educational only — "
                "not medical advice."
            ),
            tools=search_tools,
            llm=llm,
            verbose=True,
        )
        nutrition_task = Task(
            description=(
                "Analyze nutritional content of '{meal_name}' for {servings} "
                "people. Estimate calories, protein, carbs, and fats. Consider "
                "dietary restrictions: {dietary_restrictions}. Suggest healthy "
                "alternatives within {budget} if useful."
            ),
            expected_output=(
                "Nutritional analysis with calorie estimates, macronutrient "
                "breakdown, and improvement suggestions."
            ),
            agent=nutrition_analyst,
            context=[meal_planning_task, shopping_task, budget_task],
            output_file=str(OUTPUTS / "nutrition_analysis.md"),
        )
        agents.insert(-1, nutrition_analyst)
        prior_tasks.insert(-1, nutrition_task)

    nutrition_line = (
        "5. Nutrition analysis highlights\n" if include_nutrition else ""
    )
    summary_task = Task(
        description=(
            "Compile a comprehensive meal planning report that includes:\n"
            "1. Recipe and cooking instructions from the meal planner\n"
            "2. Organized shopping list with prices\n"
            "3. Budget analysis and money-saving tips\n"
            "4. Leftover / waste-reduction suggestions\n"
            f"{nutrition_line}"
            "Format as a complete, user-friendly meal planning guide."
        ),
        expected_output=(
            "A comprehensive meal planning guide combining all team outputs."
        ),
        agent=summary_agent,
        context=prior_tasks,
        output_file=str(OUTPUTS / "full_guide.md"),
    )

    return Crew(
        agents=agents,
        tasks=[*prior_tasks, summary_task],
        process=Process.sequential,
        verbose=True,
    )


def run_planner(
    meal_name: str,
    servings: int,
    budget: str,
    dietary_restrictions: str,
    cooking_skill: str,
    include_nutrition: bool = True,
) -> str:
    restrictions = [
        r.strip() for r in (dietary_restrictions or "").split(",") if r.strip()
    ] or ["none"]

    crew = build_crew(include_nutrition=include_nutrition)
    result = crew.kickoff(
        inputs={
            "meal_name": meal_name,
            "servings": int(servings),
            "budget": budget,
            "dietary_restrictions": restrictions,
            "cooking_skill": cooking_skill,
        }
    )
    return getattr(result, "raw", None) or str(result)


def run_planner_lite(
    meal_name: str,
    servings: int,
    budget: str,
    dietary_restrictions: str,
    cooking_skill: str,
    include_nutrition: bool = False,
) -> str:
    """Single LLM call for hub free-tier (avoids multi-agent TPM burn)."""
    import sys

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from langchain_core.messages import HumanMessage, SystemMessage

    from shared.llm import get_chat_llm, invoke_chat
    from shared.strip_thinking import strip_model_thinking

    diet = (dietary_restrictions or "").strip() or "none"
    nutrition_line = (
        "- Brief nutrition notes (calories/macros estimates only)\n"
        if include_nutrition
        else ""
    )
    system = (
        "You are a practical meal-planning assistant. Write clear markdown. "
        "Be concrete and concise — under 550 words. Educational grocery guidance only. "
        "Prefer numbered/bulleted lists over tables. Put a blank line between sections "
        "and between recipe steps. Never smash column headers together. "
        "Keep every section short so the full plan fits; no HTML tags."
    )
    user = (
        f"Plan a meal for:\n"
        f"- Dish: {meal_name}\n"
        f"- Servings: {servings}\n"
        f"- Budget: {budget}\n"
        f"- Dietary: {diet}\n"
        f"- Cooking skill: {cooking_skill}\n\n"
        "Include these sections as ## headings:\n"
        "1. Recipe & steps — 5–7 numbered steps; each step one short paragraph "
        "(optional leading time like `5 min — Prep: …`)\n"
        "2. Shopping list — bullets grouped by store section\n"
        "3. Budget tips — 3 short bullets\n"
        "4. Leftover ideas — 2–3 short bullets\n"
        f"{nutrition_line}"
        "Do not use markdown tables or HTML."
    )

    llm = get_chat_llm(temperature=0.3)
    # Cap completion size for free-tier Groq limits.
    if hasattr(llm, "bind"):
        try:
            llm = llm.bind(max_tokens=1200)
        except Exception:
            pass

    msg = invoke_chat(
        llm,
        [SystemMessage(content=system), HumanMessage(content=user)],
    )
    text = getattr(msg, "content", None) or str(msg)
    if isinstance(text, list):
        text = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in text
        )
    return strip_model_thinking(str(text)).strip() or str(text)
