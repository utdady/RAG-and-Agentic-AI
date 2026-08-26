# Structured Meal & Grocery Planner — original lab notes

Course: CrewAI + Pydantic structured outputs + Serper + Watsonx Granite.
Progressive crews: meal planner → + shopping → + budget → + leftovers (YAML
`LeftoversCrew`) → summary; exercise adds nutrition analyst.
Weekly schema models (`WeeklyMealPlan`, etc.) were demonstrated but not fully wired.

## Assets (course wget)

- `leftover.py` → `LeftoversCrew` (`@CrewBase`)
- `config/agents.yaml`, `config/tasks.yaml`

## This repo

Standalone Gradio app; Groq/Ollama; `SERPER_API_KEY` from `.env` (never hardcode).
