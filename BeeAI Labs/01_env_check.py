"""01 — Env check (course t1 watsonx/openai presets → repo-root .env)."""

from __future__ import annotations

from _bootstrap import banner, quiet_asyncio_logs, resolve_beeai_model_name


def main() -> None:
    quiet_asyncio_logs()
    banner("01 — BeeAI environment")
    model = resolve_beeai_model_name()
    print(f"Resolved ChatModel slug: {model}")
    print("Environment configured successfully!")
    print("(No Watsonx project ID needed — use GROQ_API_KEY or Ollama.)")


if __name__ == "__main__":
    main()
