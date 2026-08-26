"""Mental health support GroupChat (emotion analysis → self-care tips)."""

from __future__ import annotations

import warnings

from autogen import ConversableAgent, GroupChat, GroupChatManager

from formatting import DISCLAIMER_MENTAL, format_messages
from llm_config import get_llm_config

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def run_mental_health_chat(user_feelings: str) -> str:
    user_feelings = (user_feelings or "").strip()
    if not user_feelings:
        return DISCLAIMER_MENTAL + "Share how you are feeling first."

    llm_config = get_llm_config()

    patient_agent = ConversableAgent(
        name="patient",
        system_message=(
            "You describe your emotions and mental health concerns briefly. "
            "You are role-playing the user voice in a demo."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    emotion_analysis_agent = ConversableAgent(
        name="emotion_analysis",
        system_message=(
            "You analyze the user's emotions based on their input. "
            "Do not provide treatment or self-care advice. "
            "Instead, just summarize the dominant emotions they may be experiencing. "
            "This is educational only."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    therapy_recommendation_agent = ConversableAgent(
        name="therapy_recommendation",
        system_message=(
            "You suggest gentle relaxation techniques and general self-care ideas "
            "only based on the analysis from the Emotion Analysis Agent. "
            "Do not analyze emotions—just give recommendations based on the prior "
            "response. Do not claim to be a therapist. Encourage seeking professional "
            "help if distress is severe or ongoing."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    groupchat = GroupChat(
        agents=[emotion_analysis_agent, therapy_recommendation_agent],
        messages=[],
        max_round=3,
        speaker_selection_method="round_robin",
    )
    manager = GroupChatManager(name="manager", groupchat=groupchat)

    patient_agent.initiate_chat(
        manager,
        message=f"I have been feeling {user_feelings}. Can you help?",
    )

    body = format_messages(groupchat.messages)
    return DISCLAIMER_MENTAL + body
