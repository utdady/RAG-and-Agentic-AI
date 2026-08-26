"""LangChain SQL agent over local Chinook SQLite (or optional DATABASE_URL)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase

from shared.llm import get_llm_info

HERE = Path(__file__).resolve().parent
DEFAULT_DB = HERE / "data" / "Chinook.sqlite"


def _db_uri() -> str:
    override = os.getenv("DATABASE_URL", "").strip()
    if override:
        return override
    if not DEFAULT_DB.is_file():
        raise FileNotFoundError(
            f"Missing {DEFAULT_DB}. Run download_data.py or start app.py once."
        )
    # Absolute path for SQLAlchemy on Windows
    return f"sqlite:///{DEFAULT_DB.resolve().as_posix()}"


@lru_cache(maxsize=1)
def get_sql_agent():
    llm, info = get_llm_info(temperature=0.2)
    db = SQLDatabase.from_uri(_db_uri())
    try:
        agent = create_sql_agent(
            llm=llm,
            db=db,
            verbose=False,
            agent_type="tool-calling",
            handle_parsing_errors=True,
        )
    except Exception:
        from langchain.agents import AgentType

        agent = create_sql_agent(
            llm=llm,
            db=db,
            verbose=False,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
        )
    return agent, info, db


def describe_setup() -> str:
    _, info, db = get_sql_agent()
    dialect = getattr(db, "dialect", None) or "sqlite"
    return f"{info.provider}:{info.model} | dialect={dialect}"


def run_query(question: str) -> str:
    agent, _, _ = get_sql_agent()
    result = agent.invoke({"input": question})
    if isinstance(result, dict):
        return str(result.get("output") or result)
    return str(result)
