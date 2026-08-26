"""01 — Two ConversableAgents: student ↔ tutor (course AutoGen tutorial)."""

from __future__ import annotations

from autogen import ConversableAgent

from _bootstrap import banner, get_llm_config


def main() -> None:
    banner("01 — Student / tutor chat")
    llm_config = get_llm_config()

    student = ConversableAgent(
        name="student",
        system_message=(
            "You are a curious student. You ask clear, specific questions "
            "to learn new concepts."
        ),
        human_input_mode="NEVER",
        llm_config=llm_config,
    )

    tutor = ConversableAgent(
        name="tutor",
        system_message=(
            "You are a helpful tutor who provides clear and concise "
            "explanations suitable for a beginner."
        ),
        human_input_mode="NEVER",
        llm_config=llm_config,
    )

    chat_result = student.initiate_chat(
        recipient=tutor,
        message="Can you explain what a neural network is?",
        max_turns=2,
        summary_method="reflection_with_llm",
    )

    print("\nFinal Summary:")
    print(getattr(chat_result, "summary", chat_result))


if __name__ == "__main__":
    main()
