"""Load repo-root .env, then optional project .env (project overrides)."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


def load_env(project_dir: Path | None = None) -> Path:
    """
    Load environment variables.

    1. Repo root `.env` (directory containing `shared/`)
    2. `project_dir/.env` with override=True if provided

    Returns the resolved repo root path.
    """
    here = Path(project_dir).resolve() if project_dir else Path.cwd().resolve()
    root = here
    # Walk up until we find shared/ or .git
    for candidate in [here, *here.parents]:
        if (candidate / "shared").is_dir() or (candidate / ".git").is_dir():
            root = candidate
            break

    load_dotenv(root / ".env")
    if project_dir is not None:
        load_dotenv(Path(project_dir).resolve() / ".env", override=True)
    return root
