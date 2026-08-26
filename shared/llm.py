"""
Shared LLM helpers for this repo.

Default: Groq when GROQ_API_KEY is set, else Ollama (hardware-tiered model).
Override with LLM_PROVIDER=groq|ollama|auto
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache

# Conservative picks: prefer models that actually run over leaderboard winners.
OLLAMA_BY_TIER = {
    "low": "llama3.2:1b",
    "mid": "llama3.2:3b",
    "high": "llama3.1:8b",
}

WHISPER_BY_TIER = {
    "low": "openai/whisper-tiny.en",
    "mid": "openai/whisper-base.en",
    "high": "openai/whisper-small.en",
}

# Prefer these installed Ollama tags (first match wins within a tier bucket).
OLLAMA_CANDIDATES = {
    "low": ("llama3.2:1b", "gemma2:2b", "phi3:mini", "tinyllama"),
    "mid": ("llama3.2:3b", "llama3.2", "phi3:mini", "mistral:7b", "gemma2:2b"),
    "high": ("llama3.1:8b", "llama3.1", "llama3.2", "mistral:7b", "llama3.2:3b"),
}

DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


@dataclass(frozen=True)
class LLMInfo:
    provider: str
    model: str
    tier: str


@lru_cache(maxsize=1)
def detect_hardware_tier() -> str:
    """Return low | mid | high from RAM / nvidia-smi. Override with HARDWARE_TIER."""
    forced = os.getenv("HARDWARE_TIER", "").strip().lower()
    if forced in {"low", "mid", "high"}:
        return forced

    ram_gb = 8.0
    try:
        import psutil

        ram_gb = psutil.virtual_memory().total / (1024**3)
    except Exception:
        pass

    has_gpu = False
    if shutil.which("nvidia-smi"):
        try:
            proc = subprocess.run(
                ["nvidia-smi", "-L"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            has_gpu = proc.returncode == 0 and bool(proc.stdout.strip())
        except (OSError, subprocess.SubprocessError):
            has_gpu = False

    if has_gpu or ram_gb >= 16:
        return "high"
    if ram_gb >= 8:
        return "mid"
    return "low"


def _ollama_installed_names() -> set[str]:
    if not shutil.which("ollama"):
        return set()
    try:
        kwargs: dict = {
            "capture_output": True,
            "text": True,
            "timeout": 3,
            "check": False,
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        proc = subprocess.run(["ollama", "list"], **kwargs)
    except (OSError, subprocess.SubprocessError):
        return set()
    if proc.returncode != 0:
        return set()

    names: set[str] = set()
    for line in proc.stdout.splitlines()[1:]:
        parts = line.split()
        if parts:
            names.add(parts[0])
    return names


def _name_matches(installed: str, candidate: str) -> bool:
    """True if an installed tag satisfies the candidate (exact or same family)."""
    if installed == candidate:
        return True
    # e.g. installed llama3.2 matches candidate llama3.2
    inst_base = installed.split(":")[0]
    cand_base = candidate.split(":")[0]
    if ":" not in candidate and inst_base == cand_base:
        return True
    return False


def pick_ollama_model(tier: str | None = None) -> str:
    """
    Choose an Ollama model for this machine.
    OLLAMA_MODEL always wins. Else prefer an already-pulled candidate for the tier.
    """
    override = os.getenv("OLLAMA_MODEL", "").strip()
    if override:
        return override

    tier = tier or detect_hardware_tier()
    installed = _ollama_installed_names()
    for candidate in OLLAMA_CANDIDATES.get(tier, OLLAMA_CANDIDATES["mid"]):
        for name in installed:
            if _name_matches(name, candidate):
                return name

    return OLLAMA_BY_TIER.get(tier, OLLAMA_BY_TIER["mid"])


def resolve_whisper_model() -> str:
    """WHISPER_MODEL override, else tier-based Hugging Face Whisper id."""
    override = os.getenv("WHISPER_MODEL", "").strip()
    if override:
        return override
    return WHISPER_BY_TIER[detect_hardware_tier()]


def resolve_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        return "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"
    if provider not in {"groq", "ollama"}:
        raise ValueError(
            f"Unknown LLM_PROVIDER={provider!r}. Use auto, groq, or ollama."
        )
    return provider


def get_chat_llm(temperature: float = 0.5):
    """
    Return a LangChain chat model (Groq or Ollama).

    Env:
      LLM_PROVIDER=auto|groq|ollama
      GROQ_API_KEY, GROQ_MODEL
      OLLAMA_MODEL, HARDWARE_TIER=low|mid|high
    """
    provider = resolve_provider()
    tier = detect_hardware_tier()

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "LLM_PROVIDER=groq but GROQ_API_KEY is not set. "
                "Add it to .env or use LLM_PROVIDER=ollama."
            )
        from langchain_groq import ChatGroq

        model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
        return ChatGroq(model=model, temperature=temperature, api_key=api_key)

    from langchain_ollama import ChatOllama

    model = pick_ollama_model(tier)
    return ChatOllama(model=model, temperature=temperature)


def get_llm_info(temperature: float = 0.5) -> tuple[object, LLMInfo]:
    """Return (llm, info) for logging / UI."""
    provider = resolve_provider()
    tier = detect_hardware_tier()
    if provider == "groq":
        model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
    else:
        model = pick_ollama_model(tier)
    llm = get_chat_llm(temperature=temperature)
    return llm, LLMInfo(provider=provider, model=model, tier=tier)


def describe_setup() -> str:
    """Human-readable one-liner of the resolved LLM + Whisper choice."""
    provider = resolve_provider()
    tier = detect_hardware_tier()
    if provider == "groq":
        model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
    else:
        model = pick_ollama_model(tier)
    whisper = resolve_whisper_model()
    return (
        f"LLM={provider}:{model} (tier={tier}); Whisper={whisper}"
    )
