"""02 — Tools on Agent vs tools on Task (+ custom @tool calculator).

Course: Daily Dish FAQ PDFSearchTool + Serper; agent-centric vs task-centric crews.
Here: Groq/Ollama + SERPER_API_KEY from .env; local MiniLM embedder for PDF search.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import warnings
from functools import reduce
from pathlib import Path

import requests

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.env_load import load_env

load_env(ROOT)

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import tool
from crewai_tools import PDFSearchTool, SerperDevTool

FAQ_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "7vgNfis17dQfjHAiIKkBOg/The-Daily-Dish-FAQ.pdf"
)
FAQ_PATH = ROOT / "data" / "The-Daily-Dish-FAQ.pdf"


def get_crew_llm() -> LLM:
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        provider = "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise SystemExit("Set GROQ_API_KEY in repo-root .env")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        return LLM(
            model=f"groq/{model}",
            api_key=api_key,
            temperature=0.3,
            max_tokens=1500,
        )
    model = os.getenv("OLLAMA_MODEL", "llama3.2").strip() or "llama3.2"
    return LLM(
        model=f"ollama/{model}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.3,
        max_tokens=1500,
    )


def ensure_faq_pdf() -> Path:
    FAQ_PATH.parent.mkdir(parents=True, exist_ok=True)
    if FAQ_PATH.exists() and FAQ_PATH.stat().st_size > 0:
        return FAQ_PATH
    print(f"Downloading FAQ → {FAQ_PATH.name}")
    r = requests.get(FAQ_URL, timeout=120)
    r.raise_for_status()
    FAQ_PATH.write_bytes(r.content)
    return FAQ_PATH


def make_pdf_tool(pdf_path: Path) -> PDFSearchTool:
    return PDFSearchTool(
        pdf=str(pdf_path),
        config={
            "embedder": {
                "provider": "huggingface",
                "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
            }
        },
    )


def build_agent_centric_crew(llm: LLM, pdf_tool: PDFSearchTool, web: SerperDevTool) -> Crew:
    agent = Agent(
        role="The Daily Dish Inquiry Specialist",
        goal=(
            "Accurately answer customer questions about The Daily Dish restaurant. "
            "Decide whether to use the FAQ PDF or a web search."
        ),
        backstory=(
            "You are an AI assistant for The Daily Dish with a PDF FAQ tool and "
            "a web search tool. Choose the best tool for each question."
        ),
        tools=[pdf_tool, web],
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    task = Task(
        description=(
            "Answer the customer query: '{customer_query}'. "
            "Use PDF search and/or web search as needed. "
            "Synthesize a clear, friendly response."
        ),
        expected_output="A comprehensive, well-formatted answer to the query.",
        agent=agent,
    )
    return Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )


def build_task_centric_crew(llm: LLM, pdf_tool: PDFSearchTool) -> Crew:
    agent = Agent(
        role="Customer Service Specialist",
        goal="Follow a multi-step process to answer customer questions accurately.",
        backstory=(
            "You execute each task diligently. Tools are provided per task, "
            "not on the agent itself."
        ),
        tools=[],
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    faq_search = Task(
        description=(
            "Search the restaurant FAQ PDF for information related to: "
            "'{customer_query}'."
        ),
        expected_output=(
            "A relevant FAQ snippet, or a clear note that nothing was found."
        ),
        tools=[pdf_tool],
        agent=agent,
    )
    draft = Task(
        description=(
            "Using the FAQ search results, draft a friendly response to: "
            "'{customer_query}'."
        ),
        expected_output="The final customer-facing response.",
        agent=agent,
        context=[faq_search],
    )
    return Crew(
        agents=[agent],
        tasks=[faq_search, draft],
        process=Process.sequential,
        verbose=True,
    )


@tool("Add Two Numbers Tool")
def add_numbers(data: str) -> int:
    """Extract integers from text and return their sum."""
    numbers = list(map(int, re.findall(r"-?\d+", data or "")))
    return sum(numbers)


@tool("Multiply Numbers Tool")
def multiply_numbers(data: str) -> int:
    """Extract integers from text and return their product."""
    numbers = list(map(int, re.findall(r"-?\d+", data or "")))
    return reduce(lambda x, y: x * y, numbers, 1)


def build_calculator_crew(llm: LLM) -> Crew:
    agent = Agent(
        role="Calculator",
        goal="Add or multiply numbers using the Add and Multiply tools.",
        backstory="An expert at parsing numeric instructions.",
        tools=[add_numbers, multiply_numbers],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
    task = Task(
        description=(
            "Extract numbers from '{numbers}' and either add or multiply them "
            "based on the natural-language instruction."
        ),
        expected_output="An integer result (sum or product).",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], verbose=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="CrewAI tools vs tasks demos")
    parser.add_argument(
        "--mode",
        choices=["agent", "task", "calc", "all"],
        default="all",
        help="Which demo to run",
    )
    parser.add_argument(
        "--query",
        default="What are your opening hours?",
        help="Customer query for Daily Dish demos",
    )
    args = parser.parse_args()

    if not os.getenv("SERPER_API_KEY", "").strip() and args.mode in {
        "agent",
        "all",
    }:
        print("Warning: SERPER_API_KEY missing — agent-centric web search may fail.")

    llm = get_crew_llm()
    print(f"LLM: {llm.model}")
    pdf_path = ensure_faq_pdf()
    pdf_tool = make_pdf_tool(pdf_path)
    web = SerperDevTool()

    if args.mode in {"agent", "all"}:
        print("\n===== Agent-centric (tools on Agent) =====")
        crew = build_agent_centric_crew(llm, pdf_tool, web)
        print(crew.kickoff(inputs={"customer_query": args.query}))

    if args.mode in {"task", "all"}:
        print("\n===== Task-centric (tools on Task) =====")
        crew = build_task_centric_crew(llm, pdf_tool)
        print(crew.kickoff(inputs={"customer_query": args.query}))

    if args.mode in {"calc", "all"}:
        print("\n===== Custom @tool calculator =====")
        calc = build_calculator_crew(llm)
        print("Sum:", calc.kickoff(inputs={"numbers": "please add 4, 5, and 6"}))
        print(
            "Product:",
            calc.kickoff(
                inputs={"numbers": "multiply 7 and 8 also 9 dont forget 10"}
            ),
        )


if __name__ == "__main__":
    main()
