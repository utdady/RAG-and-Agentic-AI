"""Download lab assets (company policies + LangChain paper PDF)."""

from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent / "data"
ASSETS = {
    "companypolicies.txt": (
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "MZ9z1lm-Ui3YBp3SYWLTAQ/companypolicies.txt"
    ),
    "langchain-paper.pdf": (
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "ioch1wsxkfqgfLLgmd-6Rw/langchain-paper.pdf"
    ),
}


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    for name, url in ASSETS.items():
        out = DATA / name
        if out.exists() and out.stat().st_size > 0:
            print(f"Exists: {out.name}")
            continue
        print(f"Downloading {name}...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        out.write_bytes(r.content)
        print(f"Saved {out} ({len(r.content)} bytes)")


if __name__ == "__main__":
    main()
