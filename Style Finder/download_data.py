"""Download the course fashion embeddings pickle."""

from __future__ import annotations

from pathlib import Path

import requests

import config

DATA = config.DATA_DIR
OUT = config.EMBEDDINGS_PATH
URL = config.EMBEDDINGS_URL


def main() -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.stat().st_size > 0:
        print(f"Exists: {OUT.name} ({OUT.stat().st_size:,} bytes)")
        return OUT
    print(f"Downloading {OUT.name}…")
    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    OUT.write_bytes(r.content)
    print(f"Saved {OUT} ({len(r.content):,} bytes)")
    return OUT


if __name__ == "__main__":
    main()
