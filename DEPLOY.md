# Deploying the AI Lab

Split deployment: **Next.js on Vercel** + **FastAPI on Railway** (or Render/Fly).

```
Portfolio (GitHub Pages)          Vercel (web/)              Railway (api/)
utdady.github.io/ai-lab.html  →   lab.yourdomain.com    →    api.yourdomain.com
     "Try live demos" link            demo hub UI               17 SSE demos
```

## 0. Preflight (local)

From repo root, with `.env` containing `GROQ_API_KEY`:

```powershell
pip install -r api/requirements.txt -r api/requirements-demos.txt
python -m api.diagnostics.preflight --probe
```

Fix any failing imports before paying for hosting.

---

## 1. API on Railway

### Create the service

1. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → this repo.
2. Railway reads `railway.toml` and builds `api/Dockerfile` (first build may take ~10–15 min — torch + embeddings are heavy).
3. After deploy, open **Settings → Networking → Generate Domain** (e.g. `ai-lab-api-production.up.railway.app`).

### Required env vars (Railway → Variables)

| Variable | Value | Notes |
|----------|-------|-------|
| `GROQ_API_KEY` | `gsk_…` | From [console.groq.com](https://console.groq.com/keys) |
| `LLM_PROVIDER` | `groq` | Default in Docker image; set explicitly |
| `PORT` | *(auto)* | Railway injects this; Dockerfile uses it |

### Optional env vars

| Variable | When needed |
|----------|-------------|
| `SERPER_API_KEY` | CrewAI web-search demos |
| `TAVILY_API_KEY` | LangGraph search demos |
| `GOOGLE_API_KEY` | Gradio image demos |
| `GROQ_MODEL` | Override default chat model |
| `GROQ_VISION_MODEL` | Override vision model |
| `WHISPER_MODEL` | Default: `openai/whisper-tiny.en` |
| `CORS_ORIGINS` | Comma list if you tighten CORS later |

### Verify

```powershell
curl https://YOUR-RAILWAY-DOMAIN/health
```

Expect: `{"ok":true,"groq":true,"demos":17,...}`

### Docker smoke (optional, before Railway)

```powershell
docker build -f api/Dockerfile -t ai-lab-api .
docker run --env-file .env -p 8080:8080 ai-lab-api
curl http://127.0.0.1:8080/health
```

---

## 2. UI on Vercel

### Create the project

1. [vercel.com](https://vercel.com) → **Add New Project** → import this repo.
2. **Root Directory:** `web`
3. Framework preset: **Next.js** (auto-detected via `web/vercel.json`).

### Required env vars (Vercel → Settings → Environment Variables)

| Variable | Value | Environments |
|----------|-------|--------------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-RAILWAY-DOMAIN` | Production, Preview |

**Important:** Point the browser **directly** at the API URL. Do not rely on the Vercel `/api/hub` proxy for demo runs — SSE streams can exceed serverless timeouts.

### Optional env vars

| Variable | Value | Purpose |
|----------|-------|---------|
| `NEXT_PUBLIC_PORTFOLIO_URL` | `https://utdady.github.io` | “Portfolio” link in hub sidebar |
| `API_PROXY_URL` | Same Railway URL | Only if you use `/api/hub` server proxy for health checks |

### Custom domain (recommended)

Vercel → **Domains** → add e.g. `lab.utdady.dev`.

### Verify

1. Open your Vercel URL → hub home loads.
2. Open a demo (e.g. **Math Assistant**) → streaming answer appears.
3. No yellow “API offline” banner.

---

## 3. Portfolio (GitHub Pages)

Copy `docs/portfolio/ai-lab.html` into your portfolio repo (e.g. `utdady.github.io/ai-lab.html`).

Edit the template placeholders:

- `LIVE_HUB_URL` → your Vercel URL (or custom domain)
- `GITHUB_REPO_URL` → already set to this monorepo

Add a nav link on your main portfolio page:

```html
<a href="/ai-lab.html">AI Lab</a>
```

The hub shows a **Portfolio** link when `NEXT_PUBLIC_PORTFOLIO_URL` is set (defaults to `https://utdady.github.io`).

---

## 4. Env var cheat sheet

### Production only

| Where | Variable | Example |
|-------|----------|---------|
| Railway | `GROQ_API_KEY` | `gsk_…` |
| Railway | `LLM_PROVIDER` | `groq` |
| Vercel | `NEXT_PUBLIC_API_URL` | `https://ai-lab-api-production.up.railway.app` |
| Vercel | `NEXT_PUBLIC_PORTFOLIO_URL` | `https://utdady.github.io` |

### Local dev (unchanged)

```powershell
.\scripts\start_lab.ps1
```

No `NEXT_PUBLIC_API_URL` needed locally — browser uses `/api/hub` → `localhost:8080`.

---

## 5. Cost & abuse notes

- Public demos call **your Groq key** on every run. Monitor usage at Groq console.
- First request after cold start may be slow (embedding model load, Chroma init).
- Consider highlighting 5–8 demos on the portfolio page even though all 17 are in the hub.
- Later hardening: rate limits, API key gateway, or demo-only model caps.

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| “API offline” on Vercel | `NEXT_PUBLIC_API_URL` missing/wrong | Set env var, redeploy |
| CORS error in browser console | API URL typo or http vs https | Use `https://` Railway URL |
| 502 on `/api/hub` only | `API_PROXY_URL` not set on Vercel | Set it, or use `NEXT_PUBLIC_API_URL` |
| Build fails on Railway | OOM during pip install | Upgrade Railway plan or use CPU-only torch |
| `groq: false` in `/health` | `GROQ_API_KEY` not set on Railway | Add secret, redeploy |
| Demo times out | Cold start + slow demo | Retry; check Railway logs |

---

## Quick deploy checklist

- [ ] `preflight --probe` passes locally
- [ ] Railway service live, `/health` returns `ok: true`
- [ ] Vercel deployed with `NEXT_PUBLIC_API_URL`
- [ ] One chat demo + one file demo tested in production
- [ ] `ai-lab.html` on portfolio with live hub link
- [ ] Portfolio link works from hub sidebar
