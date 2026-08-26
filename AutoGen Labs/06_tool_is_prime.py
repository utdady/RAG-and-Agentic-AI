"""06 — register_function for prime-number tool calling."""

from __future__ import annotations

from typing import Annotated

from autogen import ConversableAgent, register_function

from _bootstrap import banner, get_llm_config


def is_prime(n: Annotated[int, "Positive integer"]) -> str:
    if n < 2:
        return "No"
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return "No"
    return "Yes"


def main() -> None:
    banner("06 — Tool calling (is_prime)")
    llm_config = get_llm_config()

    math_asker = ConversableAgent(
        name="math_asker",
        system_message=(
            "Ask whether a number is prime. Use the is_prime tool when needed."
        ),
        llm_config=llm_config,
    )

    math_checker = ConversableAgent(
        name="math_checker",
        human_input_mode="NEVER",
        llm_config=llm_config,
    )

    register_function(
        is_prime,
        caller=math_asker,
        executor=math_checker,
        description="Check if a number is prime. Returns Yes or No.",
    )

    math_checker.initiate_chat(
        recipient=math_asker,
        message="Is 72 a prime number?",
        max_turns=2,
    )


if __name__ == "__main__":
    main()
