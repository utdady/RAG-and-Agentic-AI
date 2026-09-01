"""Repo path, env load, Groq-only production defaults."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

os.environ.setdefault("LLM_PROVIDER", "groq")
os.environ.setdefault("WHISPER_MODEL", "openai/whisper-tiny.en")

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from shared.env_load import load_env  # noqa: E402

load_env(REPO)

_REPO_ROOT = REPO.resolve()
_KEEP_MODULE_ROOTS = frozenset({"shared", "api"})
_SKIP_DEMO_SCAN = frozenset(
    {
        "shared",
        "api",
        "web",
        "scripts",
        "node_modules",
        "__pycache__",
        ".git",
        ".pytest_cache",
    }
)
_DEMO_PACKAGE_ROOTS = frozenset(
    {
        "agent",
        "agents",
        "config",
        "document_processor",
        "retriever",
        "utils",
        "rag",
        "modules",
        "tools",
        "models",
        "download_data",
        "rag_chat",
        "shared_food",
        "crew_app",
        "healthcare_crew",
        "llm_service",
        "helpers",
        "image_processor",
    }
)


def _resolve_path(path: Path | str) -> Path:
    return Path(path).resolve()


def _promote_sys_path(path: Path) -> None:
    """Ensure this demo folder is first on sys.path (handles duplicate path strings)."""
    target = _resolve_path(path)
    sys.path[:] = [
        entry for entry in sys.path if not _path_entry_matches(entry, target)
    ]
    sys.path.insert(0, str(target))


def _path_entry_matches(entry: str, target: Path) -> bool:
    if not entry:
        return False
    try:
        return _resolve_path(entry) == target
    except OSError:
        return False


def add_app(folder: str, *, chdir: bool = True) -> Path:
    path = _resolve_path(REPO / folder)
    _promote_sys_path(path)
    if chdir:
        os.chdir(path)
    return path


def _iter_demo_dirs() -> list[Path]:
    dirs: list[Path] = []
    for child in _REPO_ROOT.iterdir():
        if not child.is_dir() or child.name.startswith("."):
            continue
        if child.name in _SKIP_DEMO_SCAN:
            continue
        dirs.append(child.resolve())
    return dirs


def _module_file(mod: object) -> Path | None:
    cached_file = getattr(mod, "__file__", None)
    if not cached_file:
        return None
    try:
        return Path(cached_file).resolve()
    except OSError:
        return None


def clear_demo_modules() -> None:
    """Drop cached imports for every demo folder so the active path wins."""
    demo_dirs = _iter_demo_dirs()
    remove: list[str] = []
    for name, mod in list(sys.modules.items()):
        if mod is None or name.startswith(("api.", "shared.")):
            continue
        mod_file = _module_file(mod)
        if mod_file is not None:
            for demo_dir in demo_dirs:
                try:
                    mod_file.relative_to(demo_dir)
                except ValueError:
                    continue
                remove.append(name)
                break
            continue
        root = name.split(".", 1)[0]
        if root in _DEMO_PACKAGE_ROOTS:
            remove.append(name)
    for name in sorted(set(remove), key=lambda item: item.count("."), reverse=True):
        sys.modules.pop(name, None)


def clear_foreign_modules(app_path: Path) -> None:
    """Backward-compatible alias — clears demo-local modules before importing."""
    del app_path
    clear_demo_modules()


def _clear_cached_app(path: Path) -> None:
    cached = sys.modules.get("app")
    if cached is None:
        return
    cached_file = _module_file(cached)
    target = _resolve_path(path)
    if cached_file is None or target not in cached_file.parents:
        del sys.modules["app"]


def prepare_demo_import(folder: str, *, chdir: bool = True) -> Path:
    """Switch demo folder and invalidate cached imports from other demos."""
    path = _resolve_path(REPO / folder)
    demo_dirs = _iter_demo_dirs()
    sys.path[:] = [
        entry
        for entry in sys.path
        if not any(
            demo != path and _path_entry_matches(entry, demo) for demo in demo_dirs
        )
    ]
    _promote_sys_path(path)
    clear_demo_modules()
    _clear_cached_app(path)
    if chdir:
        os.chdir(path)
    return path


def prepare_app_import(folder: str, *, chdir: bool = True) -> Path:
    """Ensure `import app` resolves to this demo folder, not a cached sibling app.py."""
    return prepare_demo_import(folder, chdir=chdir)


def groq_ready() -> bool:
    return bool(os.getenv("GROQ_API_KEY", "").strip())
