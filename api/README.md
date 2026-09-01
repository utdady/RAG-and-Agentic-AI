# AI Lab Demo Hub API

FastAPI wrappers around existing RAG-and-Agentic-AI apps. Public UI lives in `web/`.

## Run (from repo root)

```powershell
$env:LLM_PROVIDER = "groq"
# GROQ_API_KEY from repo-root .env
pip install -r api/requirements.txt -r api/requirements-demos.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

Health: http://127.0.0.1:8080/health

SSE: `POST /demos/{slug}/run` as `multipart/form-data` (`message`, optional `files`).

Production secrets: `GROQ_API_KEY`, `LLM_PROVIDER=groq`. Optional: `SERPER_API_KEY`. Whisper uses `WHISPER_MODEL=openai/whisper-tiny.en` by default.

CORS is open for the Vercel hub and portfolio. Set `CORS_ORIGINS` to tighten later.

**Production deploy:** see [`../DEPLOY.md`](../DEPLOY.md) — Oracle Cloud (free) or Railway. Oracle guide: [`../docs/deploy/oracle.md`](../docs/deploy/oracle.md).

PYTHONPATH must include the repo root so `shared/` and app folders import correctly (uvicorn from repo root does this via `api.bootstrap`).

## Diagnostics

From repo root (after installing requirements):

```powershell
# Verify all 17 demos can import (no LLM calls)
python -m api.diagnostics.check_deps
```

```powershell
# Fast checks: env, catalog sync, fixtures, unit adapter cases, imports
python -m api.diagnostics.preflight

# Probe each demo adapter (Groq + sub-project deps)
python -m api.diagnostics.preflight --probe
python -m api.diagnostics.preflight --probe --include-slow

# Skip slow import checks
python -m api.diagnostics.preflight --skip-imports

# Pytest (unit only)
python -m pytest api/tests/test_preflight.py api/tests/test_adapters_unit.py -q

# Live adapter smokes (Groq; fast demos only)
python -m pytest api/tests/test_adapters_live.py -m live -q

# Slow live smokes (CrewAI, vision, PDF, YouTube, Whisper…)
$env:RUN_SLOW_LAB_TESTS = "1"
python -m pytest api/tests/test_adapters_live.py -m slow -q

# HTTP SSE smoke (API must be running on :8080)
python -m api.diagnostics.smoke
python -m api.diagnostics.smoke --include-slow
python -m api.diagnostics.smoke --slug math-assistant

# All-in-one script
.\scripts\smoke_lab.ps1
.\scripts\smoke_lab.ps1 -Live
.\scripts\smoke_lab.ps1 -Live -IncludeSlow
```

Fixtures live in `api/fixtures/` (`python api/fixtures/generate.py` creates PDF/PNG/WAV if missing).
