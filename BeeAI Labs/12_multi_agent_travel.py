"""12 — Multi-agent travel planner with HandoffTool (course t12)."""

from __future__ import annotations

import asyncio
import sys

from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.tools import Tool
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.tools.search.wikipedia import WikipediaTool
from beeai_framework.tools.think import ThinkTool
from beeai_framework.tools.weather import OpenMeteoTool

from _agents import AskPermissionRequirement, ConditionalRequirement, RequirementAgent
from _bootstrap import banner, get_chat_model, quiet_asyncio_logs


async def multi_agent_travel_planner_with_language() -> None:
    llm = get_chat_model(temperature=0)

    destination_expert = RequirementAgent(
        llm=llm,
        tools=[WikipediaTool(), ThinkTool()],
        memory=UnconstrainedMemory(),
        instructions="""You are a Destination Research Expert specializing in comprehensive travel destination analysis.

        Your expertise:
        - Landmarks and tourist activities
        - Best times to visit and seasonal considerations
        - Transportation options and accessibility
        - Safety considerations and travel advisories

        Always provide detailed, factual information with clear source attribution.""",
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(
                ThinkTool,
                force_at_step=1,
                min_invocations=1,
                max_invocations=5,
                consecutive_allowed=False,
            ),
            ConditionalRequirement(
                WikipediaTool,
                only_after=[ThinkTool],
                min_invocations=1,
                max_invocations=4,
                consecutive_allowed=False,
            ),
        ],
    )

    travel_meteorologist = RequirementAgent(
        llm=llm,
        tools=[OpenMeteoTool(), ThinkTool()],
        memory=UnconstrainedMemory(),
        instructions="""You are a Travel Meteorologist specializing in weather analysis for travel planning.

        Your expertise:
        - Climate patterns and seasonal weather analysis
        - Travel-specific weather recommendations
        - Packing suggestions based on weather forecasts
        - Activity planning based on weather conditions

        Focus on actionable weather guidance for travelers.""",
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(
                ThinkTool,
                force_at_step=1,
                min_invocations=1,
                max_invocations=2,
            ),
            ConditionalRequirement(
                OpenMeteoTool,
                only_after=[ThinkTool],
                min_invocations=1,
                max_invocations=1,
            ),
        ],
    )

    language_and_culture_expert = RequirementAgent(
        llm=llm,
        tools=[WikipediaTool(), ThinkTool()],
        memory=UnconstrainedMemory(),
        instructions="""You are a Language & Cultural Expert specializing in linguistic and cultural guidance for travelers.

        Your expertise:
        - Local languages and dialects
        - Essential phrases and communication tips
        - Cultural etiquette, customs, and social norms
        - Religious and cultural sensitivities

        Always emphasize cultural sensitivity and respectful travel practices.""",
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(
                ThinkTool,
                force_at_step=1,
                min_invocations=1,
                max_invocations=3,
                consecutive_allowed=False,
            ),
        ],
    )

    handoff_to_destination = HandoffTool(
        destination_expert,
        name="DestinationResearch",
        description=(
            "Consult our Destination Research Expert for comprehensive information "
            "about travel destinations, attractions, and practical travel guidance."
        ),
    )
    handoff_to_weather = HandoffTool(
        travel_meteorologist,
        name="WeatherPlanning",
        description=(
            "Consult our Travel Meteorologist for weather forecasts, climate analysis, "
            "and weather-appropriate travel recommendations."
        ),
    )
    handoff_to_language = HandoffTool(
        language_and_culture_expert,
        name="LanguageCulturalGuidance",
        description=(
            "Consult our Language & Cultural Expert for essential phrases, cultural "
            "etiquette, and communication guidance for respectful travel."
        ),
    )

    requirements = [
        ConditionalRequirement(ThinkTool, consecutive_allowed=False),
    ]
    if AskPermissionRequirement is not None:
        requirements.append(
            AskPermissionRequirement(
                ["DestinationResearch", "WeatherPlanning", "LanguageCulturalGuidance"]
            )
        )
        print("Note: you may be prompted to approve expert handoffs.")
    else:
        print("AskPermissionRequirement unavailable — running without handoff prompts.")

    travel_coordinator = RequirementAgent(
        llm=llm,
        tools=[
            handoff_to_destination,
            handoff_to_weather,
            handoff_to_language,
            ThinkTool(),
        ],
        memory=UnconstrainedMemory(),
        instructions="""You are the Travel Coordinator, the main interface for comprehensive travel planning.

        Your role:
        - Understand traveler requirements and preferences
        - Coordinate with specialized expert agents as needed
        - Synthesize information from multiple sources
        - Create comprehensive, actionable travel recommendations

        Available Expert Agents:
        - Destination Expert: Practical destination information
        - Travel Meteorologist: Weather analysis and climate recommendations
        - Language Expert: Language tips, cultural etiquette, and communication guidance

        Coordination Process:
        1. Think about what information is needed
        2. Delegate to appropriate experts using handoff tools
        3. Synthesize into cohesive travel recommendations""",
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=requirements,
    )

    query = """I'm planning a 2-week cultural immersion trip to Japan (Tokyo and Osaka) as a first-time visitor.
    I want to experience traditional culture, visit historical sites, and interact with locals.
    I speak only English and want to be respectful of Japanese customs.
    What should I know about the destination, weather expectations, and language/cultural tips?"""

    result = await travel_coordinator.run(query)
    print(f"\nComprehensive Travel Plan:\n{result.answer.text}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("12 — Multi-agent travel planner")
    try:
        await multi_agent_travel_planner_with_language()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    asyncio.run(main())
