"""Ensure sample docs exist under data/path (course wget equivalents)."""

from __future__ import annotations

from pathlib import Path

import requests

from _bootstrap import HERE

DATA_DIR = HERE / "data" / "path"

SAMPLE_FILES = {
    "examples.txt": (
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "aNE__JjH4DLNEibuNpfDlg/examples.txt"
    ),
    "README.txt": (
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "tfoeGPInNoajVS0DSohdVg/README.txt"
    ),
}


def ensure_sample_docs() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in SAMPLE_FILES.items():
        dest = DATA_DIR / name
        if dest.is_file() and dest.stat().st_size > 0:
            continue
        print(f"Downloading {name} …")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        dest.write_bytes(r.content)
    return DATA_DIR
