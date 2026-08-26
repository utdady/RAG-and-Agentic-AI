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
    if not os.getenv("SERPER_API_KEY", "").strip():
        raise RuntimeError(
            "Set SERPER_API_KEY in repo-root .env (https://serper.dev)."
        )

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    llm = get_crew_llm()
    search = SerperDevTool()

    meal_planner = Agent(
        role="Meal Planner & Recipe Researcher",
        goal="Search for optimal recipes and create detailed meal plans",
        backstory=(
            "A skilled meal planner who researches recipes online, considering "
            "dietary needs, cooking skill, and budget."
        ),
        tools=[search],
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
        tools=[search],
        llm=llm,
        verbose=True,
    )

    meal_planning_task = Task(
        description=(
            "Search for the best '{meal_name}' recipe for {servings} people "
            "within a {budget} budget. Consider dietary restrictions: "
            "{dietary_restrictions} and cooking skill level: {cooking_skill}. "
            "Find recipes that match the skill level and provide complete "
            "ingredient lists with quantities."
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
            tools=[search],
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
