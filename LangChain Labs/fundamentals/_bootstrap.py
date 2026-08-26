"""Shared bootstrap for LangChain Labs fundamentals scripts."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
LABS = HERE.parent
ROOT = LABS.parent  # repo root

for p in (ROOT, HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from shared.env_load import load_env

load_env(HERE)


def banner(title: str) -> None:
    from shared.llm import describe_setup

    print("=" * 60)
    print(title)
    print(describe_setup())
    print("=" * 60)
