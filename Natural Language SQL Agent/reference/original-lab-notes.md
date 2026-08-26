# Natural Language SQL Agent — original lab notes

Course: Watsonx Granite + `create_sql_agent` against Skills Network **MySQL Chinook**.

## Install (course)

```
ibm-watsonx-ai, ibm-watson-machine-learning, langchain 0.2.x,
langchain-ibm, langchain-experimental, mysql-connector-python
```

## Data

```
wget …/chinook-mysql.sql
```

Lab connected with ephemeral `mysql+mysqlconnector://root:…@host:3306/Chinook`
(credentials rotated per session — **never commit**).

## Agent

```python
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentType

db = SQLDatabase.from_uri(mysql_uri)
agent_executor = create_sql_agent(
    llm=llm, db=db, verbose=True,
    handle_parsing_errors=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)
agent_executor.invoke("How many Album are there in the database?")
```

CLI wrapper: `argparse --prompt`.

## This repo

| File | Role |
|------|------|
| `download_data.py` | Chinook **SQLite** zip → `data/Chinook.sqlite` |
| `agent.py` | `create_sql_agent` (tool-calling when possible) |
| `app.py` | Gradio (port 7866) |
| `cli.py` | `--prompt` CLI |

Optional `DATABASE_URL` for MySQL/Postgres. Course MySQL passwords omitted on purpose.
