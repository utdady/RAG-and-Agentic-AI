# AI Nutrition Coach using a Multi-Agent System and Multimodal AI

Course repo: `ibm-developer-skills-network/hjybj-Smart-Nutritional-App` (branch `5-final` / `1-start`).

## Course stack

- Gradio UI (`app.py`, port 5000 in course)
- CrewAI `@CrewBase` crews: `NourishBotRecipeCrew`, `NourishBotAnalysisCrew`
- YAML `agents.yaml` / `tasks.yaml`
- Watsonx multimodal (`meta-llama/llama-4-maverick-…`) for vision tools
- Watsonx Granite for dietary filter text
- Tools: ExtractIngredients, FilterIngredients, DietaryFilter, NutrientAnalysis
- Pydantic: `RecipeSuggestionOutput`, `NutrientAnalysisOutput`
- Side exercise: BookBuddyCrew (genre + tagline from blurb) — pedagogy only, not shipped here

## This repo

**Standalone:** `NourishBot/` (not clubbed into CrewAI Labs; separate from Flask `AI Nutrition Coach/`).

| Course | Here |
|--------|------|
| Watsonx vision + Granite | Groq vision / Ollama LLaVA + Groq/Ollama text |
| CrewBase decorators | Plain `Agent`/`Task`/`Crew` + YAML configs |
| Port 5000 | Gradio **7869** |
| Hardcoded skills-network project | Repo-root `.env` |

Run: `python app.py` → http://127.0.0.1:7869
