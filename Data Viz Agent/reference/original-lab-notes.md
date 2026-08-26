# Data Viz Agent — original lab notes

Course: watsonx.ai Llama 4 Maverick + `create_pandas_dataframe_agent` on
student mathematics performance CSV; matplotlib/seaborn charts via generated code.

## Install (course)

```
ibm-watsonx-ai, langchain 0.1.x, langchain-ibm, langchain-experimental,
matplotlib, seaborn
```

## Data

```
https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/
ZNoKMJ9rssJn-QbJ49kOzA/student-mat.csv
```

## Agent

```python
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
agent = create_pandas_dataframe_agent(
    llm, df,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
    allow_dangerous_code=True,  # required in newer langchain-experimental
)
```

Inspect generated code via:
`response['intermediate_steps'][-1][0].tool_input`

## Example prompts (course)

- Row count; age > 18 filter
- Bar: gender count
- Pie: average Walc by Gender
- Box: freetime vs G3
- Scatter: Dalc/Walc vs G3; Medu/Fedu vs G3
- Bar: internet vs average G3
- Scatter: absences vs G3

## This repo

| File | Role |
|------|------|
| `download_data.py` | Fetch CSV |
| `agent.py` | Pandas agent + figure capture |
| `app.py` | Gradio chat + plot gallery (port 7865) |

Watsonx → `shared.llm`. Prefer `agent_type="tool-calling"` when supported.
