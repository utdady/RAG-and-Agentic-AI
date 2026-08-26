"""Download FoodDataSet.json for the food search labs."""

from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent / "data"
URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "sN1PIR8qp1SJ6K7syv72qQ/FoodDataSet.json"
)
OUT = DATA / "FoodDataSet.json"


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.stat().st_size > 0:
        print(f"Exists: {OUT}")
        return
    print("Downloading FoodDataSet.json...")
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    OUT.write_bytes(r.content)
    print(f"Saved {OUT} ({len(r.content)} bytes)")


if __name__ == "__main__":
    main()
