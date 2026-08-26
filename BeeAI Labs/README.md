# BeeAI Labs

Curriculum labs for the **BeeAI Framework** (`RequirementAgent`, tools, requirements, handoffs).

Course Watsonx / OpenAI → **Groq / Ollama** via `ChatModel.from_name("groq:…")` or `ollama:…`.

## Setup

```powershell
cd "BeeAI Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env`: `GROQ_API_KEY` (preferred) or Ollama. Optional `BEEAI_MODEL=groq:llama-3.1-8b-instant`.

## Run

```powershell
python 01_env_check.py
python 02_basic_chat.py
python 03_prompt_templates.py
python 04_structured_output.py
python 05_minimal_agent.py
python 06_wikipedia_agent.py
python 07_think_wikipedia.py
python 08_controlled_requirements.py
python 09_force_think_after_tools.py
python 10_ask_permission.py
python 11_custom_calculator_tool.py
python 12_multi_agent_travel.py
```

Labs **10** and **12** may prompt in the terminal to approve tool / handoff use (`AskPermissionRequirement`).

## Scripts

| Script | Topic (course tN) |
|--------|-------------------|
| `01_env_check.py` | Env / model slug (t1) |
| `02_basic_chat.py` | ChatModel chat (t2) |
| `03_prompt_templates.py` | Mustache-style templates (t3) |
| `04_structured_output.py` | Pydantic business plan (t4) |
| `05_minimal_agent.py` | RequirementAgent, no tools (t5) |
| `06_wikipedia_agent.py` | Wikipedia + trajectory (t6) |
| `07_think_wikipedia.py` | ThinkTool + Wikipedia (t7) |
| `08_controlled_requirements.py` | ConditionalRequirement order (t8) |
| `09_force_think_after_tools.py` | force_after=Tool (t9) |
| `10_ask_permission.py` | AskPermissionRequirement (t10) |
| `11_custom_calculator_tool.py` | Custom Tool subclass (t11) |
| `12_multi_agent_travel.py` | HandoffTool multi-agent (t12) |

Helpers: `_bootstrap.py` (model + create/run compatibility), `_agents.py` (import shims), `_cyber.py` (shared analyst prompt).

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
