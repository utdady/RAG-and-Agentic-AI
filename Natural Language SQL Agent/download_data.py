"""Download Chinook SQLite DB (local stand-in for course MySQL Chinook)."""

from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent / "data"
DB_PATH = DATA / "Chinook.sqlite"

# Official Chinook SQLite sample (not the Skills Network MySQL dump)
CHINOOK_ZIP_URL = (
    "https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip"
)


def main() -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
        print(f"Exists: {DB_PATH}")
        return DB_PATH

    print("Downloading Chinook SQLite…")
    r = requests.get(CHINOOK_ZIP_URL, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(BytesIO(r.content)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith((".db", ".sqlite"))]
        if not names:
            raise RuntimeError(f"No sqlite file in zip; entries={zf.namelist()}")
        target = names[0]
        DB_PATH.write_bytes(zf.read(target))
    print(f"Saved {DB_PATH} ({DB_PATH.stat().st_size} bytes)")
    return DB_PATH


if __name__ == "__main__":
    main()
