# AI Powered Data Analysis — original lab notes

Course: OpenAI tool-calling agent that inspects CSVs and runs sklearn
classification / regression. Notebook CLI chat loop.

## Install (course)

```
langchain-openai, langchain, openai, pandas, numpy,
matplotlib, seaborn, scikit-learn
```

Matplotlib/seaborn were installed but unused in the pasted cells.

## Data

```
wget .../regression-dataset.csv
wget .../classification-dataset.csv
```

**This repo:** `download_data.py` → `data/`.

## Tools (course)

1. `list_csv_files` — `glob("*.csv")` in cwd  
2. `preload_datasets` — global `DATAFRAME_CACHE`  
3. `get_dataset_summaries` — columns + dtypes  
4. `call_dataframe_method` — arbitrary `getattr(df, method)()`  
5. `evaluate_classification_dataset` — RandomForestClassifier + accuracy  
6. `evaluate_regression_dataset` — RandomForestRegressor + R² / MSE  

Notebook bug: regression tool used `RandomForestRegressor` / `r2_score` /
`mean_squared_error` without importing them; `DATAFRAME_CACHE` was redefined mid-lab.

## Agent (course)

```python
ChatPromptTemplate + create_openai_tools_agent(llm, tools, prompt)
AgentExecutor(..., handle_parsing_errors=True)
init_chat_model("gpt-4o-mini", model_provider="openai")
```

Interactive `while True: input(...)` loop.

**This repo:** LangGraph `create_react_agent` + Groq/Ollama; Gradio UI;
`call_dataframe_method` whitelisted to safe inspection methods only;
CSVs resolved under `data/`.

## Product layout

| File | Role |
|------|------|
| `download_data.py` | Fetch course CSVs |
| `tools.py` | Tools + cache + system prompt |
| `agent.py` | Cached LangGraph agent |
| `app.py` | Gradio (port 7864) |
