"""Pandas dataframe agent + matplotlib figure capture."""

from __future__ import annotations

import io
from functools import lru_cache
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd
from langchain_experimental.agents.agent_toolkits import (  # noqa: E402
    create_pandas_dataframe_agent,
)
from PIL import Image  # noqa: E402

from shared.llm import get_llm_info  # noqa: E402

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "data" / "student-mat.csv"

PREFIX = (
    "You are a pandas and matplotlib agent working on the student-mat dataframe `df`. "
    "Use Action/Action Input/Final Answer format when required by the agent. "
    "For charts, create matplotlib figures (do not call plt.show()). "
    "Prefer clear labels and titles. Never invent columns that are not in df."
)


@lru_cache(maxsize=1)
def load_dataframe() -> pd.DataFrame:
    if not CSV_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {CSV_PATH}. Run download_data.py or start app.py once."
        )
    # Course file is comma-separated; fall back to ';' (UCI classic)
    try:
        df = pd.read_csv(CSV_PATH)
        if df.shape[1] == 1 and ";" in str(df.columns[0]):
            df = pd.read_csv(CSV_PATH, sep=";")
    except Exception:
        df = pd.read_csv(CSV_PATH, sep=";")
    return df


@lru_cache(maxsize=1)
def get_agent():
    llm, info = get_llm_info(temperature=0)
    df = load_dataframe()
    # tool-calling works best with Groq/OpenAI-style chat models; fall back if needed
    try:
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=False,
            allow_dangerous_code=True,
            agent_type="tool-calling",
            return_intermediate_steps=True,
            prefix=PREFIX,
        )
    except Exception:
        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=False,
            allow_dangerous_code=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            prefix=PREFIX,
        )
    return agent, info, df


def describe_agent() -> str:
    _, info, df = get_agent()
    return f"{info.provider}:{info.model} | df={df.shape[0]}×{df.shape[1]}"


def _capture_figures() -> list[Image.Image]:
    images: list[Image.Image] = []
    for num in plt.get_fignums():
        fig = plt.figure(num)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
        buf.seek(0)
        images.append(Image.open(buf).copy())
        buf.close()
    plt.close("all")
    return images


def _code_snippets(response: dict) -> str:
    steps = response.get("intermediate_steps") or []
    snippets: list[str] = []
    for step in steps:
        try:
            action = step[0]
            code = getattr(action, "tool_input", None)
            if isinstance(code, dict):
                code = code.get("query") or code.get("code") or str(code)
            if code:
                snippets.append(str(code).replace("; ", "\n"))
        except Exception:
            continue
    if not snippets:
        return ""
    return "\n\n--- generated code ---\n" + "\n\n".join(snippets[-3:])


def run_query(question: str) -> tuple[str, list[Image.Image]]:
    """
    Run the pandas agent. Returns (answer_text, list of plot images).

    WARNING: allow_dangerous_code=True — the LLM can execute Python against df.
    """
    agent, _, _ = get_agent()
    plt.close("all")
    response = agent.invoke({"input": question})
    if isinstance(response, dict):
        output = str(response.get("output") or response)
        extra = _code_snippets(response)
    else:
        output = str(response)
        extra = ""
    images = _capture_figures()
    return output + extra, images
