"""Build NourishBot recipe and nutrient-analysis crews."""

from __future__ import annotations

from pathlib import Path

import yaml
from crewai import Agent, Crew, Process, Task

from llm_config import get_crew_llm
from models import NutrientAnalysisOutput, RecipeSuggestionOutput
from tools import (
    analyze_image,
    extract_ingredients,
    filter_based_on_restrictions,
    filter_ingredients,
)

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config"


def _load_yaml(name: str) -> dict:
    with open(CONFIG / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _agent_kwargs(cfg: dict) -> dict:
    return {
        "role": str(cfg["role"]).strip(),
        "goal": str(cfg["goal"]).strip(),
        "backstory": str(cfg["backstory"]).strip(),
    }


def build_recipe_crew() -> Crew:
    agents_cfg = _load_yaml("agents.yaml")
    tasks_cfg = _load_yaml("tasks.yaml")
    llm = get_crew_llm()

    detector = Agent(
        **_agent_kwargs(agents_cfg["ingredient_detection_agent"]),
        tools=[extract_ingredients, filter_ingredients],
        llm=llm,
        allow_delegation=False,
        max_iter=5,
        verbose=True,
    )
    dietitian = Agent(
        **_agent_kwargs(agents_cfg["dietary_filtering_agent"]),
        tools=[filter_based_on_restrictions],
        llm=llm,
        allow_delegation=False,
        max_iter=6,
        verbose=True,
    )
    chef = Agent(
        **_agent_kwargs(agents_cfg["recipe_suggestion_agent"]),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    detect_task = Task(
        description=tasks_cfg["ingredient_detection_task"]["description"],
        expected_output=tasks_cfg["ingredient_detection_task"]["expected_output"],
        agent=detector,
    )
    filter_task = Task(
        description=tasks_cfg["dietary_filtering_task"]["description"],
        expected_output=tasks_cfg["dietary_filtering_task"]["expected_output"],
        agent=dietitian,
        context=[detect_task],
    )
    recipe_task = Task(
        description=tasks_cfg["recipe_suggestion_task"]["description"],
        expected_output=tasks_cfg["recipe_suggestion_task"]["expected_output"],
        agent=chef,
        context=[filter_task],
        output_pydantic=RecipeSuggestionOutput,
    )

    return Crew(
        agents=[detector, dietitian, chef],
        tasks=[detect_task, filter_task, recipe_task],
        process=Process.sequential,
        verbose=True,
    )


def build_analysis_crew() -> Crew:
    agents_cfg = _load_yaml("agents.yaml")
    tasks_cfg = _load_yaml("tasks.yaml")
    llm = get_crew_llm()

    analyst = Agent(
        **_agent_kwargs(agents_cfg["nutrient_analysis_agent"]),
        tools=[analyze_image],
        llm=llm,
        allow_delegation=False,
        max_iter=4,
        verbose=True,
    )
    analysis_task = Task(
        description=tasks_cfg["nutrient_analysis_task"]["description"],
        expected_output=tasks_cfg["nutrient_analysis_task"]["expected_output"],
        agent=analyst,
        output_pydantic=NutrientAnalysisOutput,
    )

    return Crew(
        agents=[analyst],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=True,
    )


def run_recipe(*, image_path: str, dietary_restrictions: str = "") -> dict:
    crew = build_recipe_crew()
    result = crew.kickoff(
        inputs={
            "uploaded_image": image_path,
            "dietary_restrictions": dietary_restrictions or "",
        }
    )
    if hasattr(result, "pydantic") and result.pydantic is not None:
        return result.pydantic.model_dump()
    if hasattr(result, "json_dict") and result.json_dict:
        return result.json_dict
    if hasattr(result, "to_dict"):
        return result.to_dict()
    return {"raw": str(result)}


def run_analysis(*, image_path: str) -> dict:
    crew = build_analysis_crew()
    result = crew.kickoff(
        inputs={
            "uploaded_image": image_path,
            "dietary_restrictions": "",
        }
    )
    if hasattr(result, "pydantic") and result.pydantic is not None:
        return result.pydantic.model_dump()
    if hasattr(result, "json_dict") and result.json_dict:
        return result.json_dict
    if hasattr(result, "to_dict"):
        return result.to_dict()
    return {"raw": str(result)}
