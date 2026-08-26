"""Download student-mat.csv (course Data Viz Agent dataset)."""

from __future__ import annotations

from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent / "data"
URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "ZNoKMJ9rssJn-QbJ49kOzA/student-mat.csv"
)
OUT = DATA / "student-mat.csv"


def main() -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.stat().st_size > 0:
        print(f"Exists: {OUT}")
        return OUT
    print("Downloading student-mat.csv...")
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    OUT.write_bytes(r.content)
    print(f"Saved {OUT} ({len(r.content)} bytes)")
    return OUT


if __name__ == "__main__":
    main()
