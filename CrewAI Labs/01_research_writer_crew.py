"""01 — CrewAI sequential multi-agent: research → blog → social posts.

Course: Watsonx Llama via crewai.LLM + SerperDevTool.
Here: Groq/Ollama via CrewAI LLM + SERPER_API_KEY from .env (never hardcode keys).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent  # CrewAI Labs/
REPO_ROOT = ROOT.parent  # repo root
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.env_load import load_env

load_env(ROOT)

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import SerperDevTool


def get_crew_llm() -> LLM:
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        provider = "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise SystemExit("Set GROQ_API_KEY in repo-root .env")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        # LiteLLM-style CrewAI model id
        return LLM(
            model=f"groq/{model}",
            api_key=api_key,
            temperature=0.4,
            max_tokens=2000,
        )

    model = os.getenv("OLLAMA_MODEL", "llama3.2").strip() or "llama3.2"
    return LLM(
        model=f"ollama/{model}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.4,
        max_tokens=2000,
    )


def build_crew(llm: LLM, with_social: bool = True) -> Crew:
    if not os.getenv("SERPER_API_KEY", "").strip():
        raise SystemExit(
            "Set SERPER_API_KEY in repo-root .env (https://serper.dev). "
            "Do not hardcode keys in source."
        )

    search_tool = SerperDevTool()

    research_agent = Agent(
        role="Senior Research Analyst",
        goal=(
            "Uncover cutting-edge information and insights on any subject "
            "with comprehensive analysis"
        ),
        backstory=(
            "You are an expert researcher with extensive experience gathering, "
            "analyzing, and synthesizing information across domains. You excel "
            "at finding reliable sources and separating fact from opinion."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool],
    )

    writer_agent = Agent(
        role="Tech Content Strategist",
        goal="Craft well-structured and engaging content based on research findings",
        backstory=(
            "You are a skilled content strategist known for translating complex "
            "topics into clear narratives for a tech-savvy audience."
        ),
        verbose=True,
        llm=llm,
        allow_delegation=False,
    )

    research_task = Task(
        description=(
            "Analyze the major {topic}, identifying key trends and technologies. "
            "Provide a detailed report on their potential impact."
        ),
        agent=research_agent,
        expected_output=(
            "A detailed report on {topic}, including trends, emerging "
            "technologies, and their impact."
        ),
    )

    writer_task = Task(
        description=(
            "Create an engaging blog post based on the research findings about "
            "{topic}. Tailor the content for a tech-savvy audience."
        ),
        agent=writer_agent,
        expected_output=(
            "A 4-paragraph blog post on {topic}, written clearly and engagingly."
        ),
    )

    agents = [research_agent, writer_agent]
    tasks = [research_task, writer_task]

    if with_social:
        social_agent = Agent(
            role="Social Media Strategist",
            goal="Generate engaging social media snippets based on the full article",
            backstory=(
                "A digital storyteller who crafts compelling posts to drive "
                "engagement and traffic."
            ),
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )
        social_task = Task(
            description=(
                "Summarize the blog post about {topic} into 2–3 engaging social "
                "media posts suitable for LinkedIn or Twitter. Informative, "
                "professional, and encouraging further reading."
            ),
            agent=social_agent,
            expected_output=(
                "A series of 2–3 well-written social posts highlighting key insights."
            ),
        )
        agents.append(social_agent)
        tasks.append(social_task)

    return Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="CrewAI research → writer → social")
    parser.add_argument(
        "--topic",
        default="Latest Generative AI breakthroughs",
        help="Topic for the crew",
    )
    parser.add_argument(
        "--no-social",
        action="store_true",
        help="Run only research + writer (2 agents)",
    )
    args = parser.parse_args()

    llm = get_crew_llm()
    print(f"Crew LLM: {llm.model}")
    crew = build_crew(llm, with_social=not args.no_social)
    result = crew.kickoff(inputs={"topic": args.topic})

    print("\n===== Final output =====\n")
    print(getattr(result, "raw", result))

    tasks_outputs = getattr(result, "tasks_output", None) or []
    for i, tout in enumerate(tasks_outputs):
        print(f"\n----- Task {i}: {getattr(tout, 'agent', '')} -----")
        print(getattr(tout, "raw", tout))

    usage = getattr(result, "token_usage", None)
    if usage:
        print("\n===== Token usage =====")
        print(f"total={getattr(usage, 'total_tokens', usage)}")
        print(f"prompt={getattr(usage, 'prompt_tokens', '?')}")
        print(f"completion={getattr(usage, 'completion_tokens', '?')}")


if __name__ == "__main__":
    main()
