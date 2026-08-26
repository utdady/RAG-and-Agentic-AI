"""Download course regression/classification CSVs into ./data."""

from __future__ import annotations

from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent / "data"

FILES = {
    "regression-dataset.csv": (
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "N0CceRlquaf9q85PK759WQ/regression-dataset.csv"
    ),
    "classification-dataset.csv": (
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "7J73m6Nsz-vmojwab91gMA/classification-dataset.csv"
    ),
}


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        out = DATA / name
        if out.exists() and out.stat().st_size > 0:
            print(f"Exists: {out}")
            continue
        print(f"Downloading {name}...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        out.write_bytes(r.content)
        print(f"Saved {out} ({len(r.content)} bytes)")


if __name__ == "__main__":
    main()
