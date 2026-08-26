"""04 — Bug triage with human-in-the-loop (human_input_mode=ALWAYS)."""

from __future__ import annotations

import random

from autogen import ConversableAgent

from _bootstrap import banner, get_llm_config

BUGS = [
    "App crashes when opening user profile.",
    "Minor UI misalignment on settings page.",
    "Password reset email not sent consistently.",
    "Typo in the About Us footer text.",
    "Database connection timeout under heavy load.",
    "Login form allows SQL injection attack.",
]

TRIAGE_SYSTEM = """
You are a bug triage assistant. You will be given bug report summaries.

For each bug:
- If it is urgent (e.g., 'crash', 'security', or 'data loss' is mentioned), escalate it and ask the human agent for confirmation.
- If it seems minor (e.g., cosmetic, typo), suggest closing it but still ask for human review.
- Otherwise, classify it as medium priority and ask the human for review.

Once all bugs are processed, summarize what was escalated, closed, or marked as medium priority.
End by saying: "You can type exit to finish."
"""


def main() -> None:
    banner("04 — Bug triage (human input)")
    print("Interactive: type replies when prompted; type 'exit' to finish.\n")
    llm_config = get_llm_config()

    triage_bot = ConversableAgent(
        name="triage_bot",
        system_message=TRIAGE_SYSTEM,
        llm_config=llm_config,
    )

    human = ConversableAgent(
        name="human",
        human_input_mode="ALWAYS",
    )

    selected = BUGS[:]
    random.shuffle(selected)
    selected = selected[:3]

    initial_prompt = (
        "Please triage the following bug reports one by one:\n\n"
        + "\n".join(f"{i + 1}. {bug}" for i, bug in enumerate(selected))
    )

    human.initiate_chat(
        recipient=triage_bot,
        message=initial_prompt,
    )


if __name__ == "__main__":
    main()
