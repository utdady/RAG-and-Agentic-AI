"""CLI: python cli.py --prompt \"How many albums?\" """

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shared.env_load import load_env

load_env(HERE)

from download_data import main as download_chinook

if not os.getenv("DATABASE_URL", "").strip():
    download_chinook()

from agent import run_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Natural Language SQL Agent CLI")
    parser.add_argument("--prompt", type=str, required=True, help="Question for the SQL agent")
    args = parser.parse_args()
    print(run_query(args.prompt))


if __name__ == "__main__":
    main()
