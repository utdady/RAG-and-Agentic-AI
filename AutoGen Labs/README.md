# AutoGen Labs (AG2)

Curriculum labs for **AG2** (formerly AutoGen): `ConversableAgent`, code execution,
group chat, tools, structured output.

Course OpenAI `gpt-4o-mini` → **Groq** (`api_type: groq`) or **Ollama** (OpenAI-compatible).

Package: `ag2` **`<1`** (imports still use `autogen`). Do not install `ag2` 1.x — that release is a different API.

## Setup

```powershell
cd "AutoGen Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env`: `GROQ_API_KEY` (preferred) or Ollama.

## Run

```powershell
python 01_student_tutor.py
python 02_specialized_agents.py
python 03_code_execution_plot.py
python 04_bug_triage_human.py
python 05_groupchat_lesson.py
python 06_tool_is_prime.py
python 07_structured_ticket.py
```

Lab **04** is interactive (`human_input_mode=ALWAYS`) — type replies; `exit` to finish.

Lab **03** writes `coding/sine_wave.png` via `LocalCommandLineCodeExecutor`.

## Scripts

| Script | Topic |
|--------|--------|
| `01_student_tutor.py` | Two-agent chat + LLM summary |
| `02_specialized_agents.py` | Tech / creative / business personas |
| `03_code_execution_plot.py` | Assistant + UserProxy code exec |
| `04_bug_triage_human.py` | Human-in-the-loop triage |
| `05_groupchat_lesson.py` | GroupChat + GroupChatManager |
| `06_tool_is_prime.py` | `register_function` tool calling |
| `07_structured_ticket.py` | Pydantic `response_format` |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
