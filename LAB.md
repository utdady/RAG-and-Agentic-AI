# AI Lab hub

Live demos: Next.js UI in [`web/`](web/) + FastAPI in [`api/`](api/).

## One command (Windows)

From repo root:

```powershell
.\scripts\start_lab.ps1
```

Opens two windows (API + UI), waits until both are healthy, then prints URLs. Options:

- `.\scripts\start_lab.ps1 -OpenBrowser` — also open the hub in your browser
- `.\scripts\start_lab.ps1 -NoKill` — do not stop existing processes on 8080/3000

## Manual

```powershell
# API (repo root)
$env:LLM_PROVIDER = "groq"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080

# UI
cd web
npm run dev:hub
```

Hub: http://localhost:3000 — API calls go through `/api/hub` (proxied to :8080).

**Deploy:** see [`DEPLOY.md`](DEPLOY.md) (Vercel + Railway checklist).

Portfolio landing page template: [`docs/portfolio/ai-lab.html`](docs/portfolio/ai-lab.html) → copy to `utdady.github.io/ai-lab.html`.
