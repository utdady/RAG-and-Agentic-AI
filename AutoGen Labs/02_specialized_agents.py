"""02 — Specialized agent personas (tech / creative / business)."""

from __future__ import annotations

from autogen import ConversableAgent

from _bootstrap import banner, get_llm_config


def main() -> None:
    banner("02 — Specialized agents")
    llm_config = get_llm_config()

    tech_expert = ConversableAgent(
        name="tech_expert",
        system_message=(
            "You are a senior software engineer with expertise in Python, AI, "
            "and system design. Provide technical, detailed explanations with "
            "code examples when appropriate. Always consider best practices "
            "and performance implications."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    creative_writer = ConversableAgent(
        name="creative_writer",
        system_message=(
            "You are a creative writer and storyteller. Your responses are "
            "engaging, imaginative, and use vivid descriptions. You excel at "
            "making complex topics accessible through stories and analogies."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    business_analyst = ConversableAgent(
        name="business_analyst",
        system_message=(
            "You are a business analyst focused on ROI, efficiency, and "
            "strategic planning. Always consider business impact, costs, and "
            "practical implementation. Provide actionable recommendations "
            "with clear metrics."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    agents = [tech_expert, creative_writer, business_analyst]
    print("Specialized agents created!")
    for agent in agents:
        first = agent.system_message.split(".")[0]
        print(f"- {agent.name}: {first}.")

    # Short demo: creative writer answers a tech prompt (persona contrast)
    result = tech_expert.initiate_chat(
        recipient=creative_writer,
        message=(
            "Explain what an API gateway is — but make it vivid and memorable "
            "for a non-engineer."
        ),
        max_turns=1,
    )
    print("\nSample reply (creative_writer):")
    print(getattr(result, "summary", result))


if __name__ == "__main__":
    main()
