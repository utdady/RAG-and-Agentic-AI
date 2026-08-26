"""05 — GroupChat lesson planner / reviewer / teacher."""

from __future__ import annotations

from autogen import ConversableAgent, GroupChat, GroupChatManager

from _bootstrap import banner, get_llm_config


def main() -> None:
    banner("05 — GroupChat lesson plan")
    llm_config = get_llm_config()

    lesson_planner = ConversableAgent(
        name="planner_agent",
        system_message="Create a short lesson plan for 4th graders.",
        description="Makes lesson plans.",
        llm_config=llm_config,
    )

    lesson_reviewer = ConversableAgent(
        name="reviewer_agent",
        system_message="Review a plan and suggest up to 3 brief edits.",
        description="Reviews lesson plans and suggests edits.",
        llm_config=llm_config,
    )

    teacher = ConversableAgent(
        name="teacher_agent",
        system_message="Suggest a topic and reply DONE when satisfied.",
        llm_config=llm_config,
        is_termination_msg=lambda x: "DONE" in (x.get("content", "") or "").upper(),
    )

    groupchat = GroupChat(
        agents=[teacher, lesson_planner, lesson_reviewer],
        messages=[],
        max_round=6,
        speaker_selection_method="auto",
    )

    manager = GroupChatManager(
        name="group_manager",
        groupchat=groupchat,
        llm_config=llm_config,
    )

    result = teacher.initiate_chat(
        recipient=manager,
        message="Make a simple lesson about the moon.",
        max_turns=6,
        summary_method="reflection_with_llm",
    )

    print("\nFinal Summary:")
    print(getattr(result, "summary", result))


if __name__ == "__main__":
    main()
