"""Physical symptom consultation GroupChat (diagnosis → pharmacy → consultation)."""

from __future__ import annotations

import warnings

from autogen import ConversableAgent, GroupChat, GroupChatManager

from formatting import DISCLAIMER_HEALTH, format_messages
from llm_config import get_llm_config

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def run_healthcare_consultation(symptoms: str) -> str:
    symptoms = (symptoms or "").strip()
    if not symptoms:
        return DISCLAIMER_HEALTH + "Describe your symptoms first."

    llm_config = get_llm_config()

    patient_agent = ConversableAgent(
        name="patient",
        system_message=(
            "You describe symptoms and ask for medical help. "
            "You are role-playing a patient; keep messages brief."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    diagnosis_agent = ConversableAgent(
        name="diagnosis",
        system_message=(
            "You analyze symptoms and provide a possible educational diagnosis "
            "hypothesis only. Summarize key points in one response. "
            "Always remind the user this is not a real medical diagnosis."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    pharmacy_agent = ConversableAgent(
        name="pharmacy",
        system_message=(
            "You discuss common over-the-counter options that people sometimes "
            "consider for similar symptoms, for educational purposes only. "
            "Do not prescribe. Only respond once. Remind users to consult a pharmacist "
            "or doctor before taking any medication."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    consultation_agent = ConversableAgent(
        name="consultation",
        system_message=(
            "You determine whether an in-person doctor's visit seems advisable "
            "(educational triage only). Provide a final summary with clear next steps. "
            "IMPORTANT: End your response with 'CONSULTATION_COMPLETE'."
        ),
        llm_config=llm_config,
        human_input_mode="NEVER",
        is_termination_msg=lambda x: "CONSULTATION_COMPLETE"
        in (x.get("content", "") or "").upper(),
    )

    groupchat = GroupChat(
        agents=[diagnosis_agent, pharmacy_agent, consultation_agent],
        messages=[],
        max_round=5,
        speaker_selection_method="round_robin",
    )
    manager = GroupChatManager(name="manager", groupchat=groupchat)

    patient_agent.initiate_chat(
        manager,
        message=f"I am feeling {symptoms}. Can you help?",
    )

    body = format_messages(groupchat.messages)
    return DISCLAIMER_HEALTH + body
