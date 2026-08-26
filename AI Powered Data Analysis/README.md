# AI Powered Data Analysis

Gradio chat: LangGraph agent explores course CSVs, inspects DataFrames, and runs RandomForest classification / regression.

- **LLM:** Groq / Ollama via [`../shared/llm.py`](../shared/llm.py)
- **Not OpenAI** — course used `gpt-4o-mini` + `create_openai_tools_agent`
- Datasets: `regression-dataset.csv`, `classification-dataset.csv` (auto-downloaded into `data/`)

## Setup

```powershell
cd "AI Powered Data Analysis"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ensure `GROQ_API_KEY` (or Ollama) in repo-root `.env`.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7864

Datasets download on first run (or `python download_data.py`).

## Tools

| Tool | Role |
|------|------|
| `list_csv_files` | CSVs in `data/` |
| `preload_datasets` | Cache DataFrames |
| `get_dataset_summaries` | Columns + dtypes |
| `call_dataframe_method` | Whitelisted: head, tail, describe, info, … |
| `evaluate_classification_dataset` | RF classifier accuracy |
| `evaluate_regression_dataset` | RF regressor R² + MSE |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
