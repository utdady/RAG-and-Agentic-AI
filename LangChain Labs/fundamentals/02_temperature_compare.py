"""02 — Temperature: creative vs precise (same model, two settings)."""

from __future__ import annotations

from _bootstrap import banner
from shared.llm import get_chat_llm, get_llm_info

banner("02 Temperature compare")
_, info = get_llm_info(temperature=0.2)
print(f"Base model {info.provider}:{info.model}\n")

prompt = (
    "Write one short product slogan for a reusable water bottle. "
    "One sentence only."
)

creative = get_chat_llm(temperature=0.8)
precise = get_chat_llm(temperature=0.1)

print("--- creative (temp=0.8) ---")
print(creative.invoke(prompt).content)

print("\n--- precise (temp=0.1) ---")
print(precise.invoke(prompt).content)
print(
    "\nNote: original lab compared Granite + Llama on Watsonx; "
    "here we reuse one Groq/Ollama model at two temperatures."
)
