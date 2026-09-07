# Deploying the AI Lab

**Recommended:** **Oracle Cloud Always Free** (API) + **Vercel** (UI) + **GitHub Pages** (portfolio).

| Piece | Host | Cost |
|-------|------|------|
| API (`api/`) | Oracle Ampere A1 VM + Docker | $0/mo |
| UI (`web/`) | Vercel | $0/mo |
| Landing page | `utdady.github.io/ai-lab.html` | $0/mo |

**Full Oracle walkthrough:** [`docs/deploy/oracle.md`](docs/deploy/oracle.md)

```
Portfolio              Vercel (web/)              Oracle VM
utdady.github.io  →    lab.vercel.app        →    https://api.yourdomain.com
```

---

## 0. Preflight (local)

From repo root, with `.env` containing `GROQ_API_KEY`:

```powershell
pip install -r api/requirements.txt -r api/requirements-demos.txt
python -m api.diagnostics.preflight --probe
```

---

## 1. API on Oracle Cloud (recommended)

See **[`docs/deploy/oracle.md`](docs/deploy/oracle.md)** for the full step-by-step.

**Short version:**

1. Create **Ampere A1** Ubuntu VM (2 OCPU / 12 GB RAM).
2. Open ports **22, 80, 443** in OCI security list.
3. SSH in → `bash scripts/oracle/setup-vm.sh`
4. Set `GROQ_API_KEY` in `.env` → `bash scripts/oracle/deploy-api.sh`
5. Put **nginx + certbot** (or Cloudflare Tunnel) in front for **HTTPS**.
6. `curl https://your-api-domain/health` → `"ok": true`

Files: `docker-compose.yml`, `scripts/oracle/*`, `api/Dockerfile`

---

## 2. UI on Vercel

1. [vercel.com](https://vercel.com) → import repo → **Root Directory:** `web`
2. Environment variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-api-domain` (must be HTTPS) |
| `NEXT_PUBLIC_PORTFOLIO_URL` | `https://aditya-bhaskar.vercel.app` |

3. Deploy → test **Math Assistant** on the live URL.

Point the browser **directly** at the API URL (not the Vercel `/api/hub` proxy) for SSE demos.

---

## 3. Portfolio

Copy `docs/portfolio/ai-lab.html` to your portfolio repo. Set `LIVE_HUB_URL` to your Vercel URL.

---

## 4. Env var cheat sheet

| Where | Variable | Example |
|-------|----------|---------|
| Oracle VM `.env` | `GROQ_API_KEY` | `gsk_…` |
| Oracle VM `.env` | `LLM_PROVIDER` | `groq` |
| Vercel | `NEXT_PUBLIC_API_URL` | `https://api.lab.yourdomain.com` |
| Vercel | `NEXT_PUBLIC_PORTFOLIO_URL` | `https://aditya-bhaskar.vercel.app` |

---

## 5. Alternative: Render (while Oracle is pending)

1. [render.com](https://render.com) → **New → Web Service** → this GitHub repo.
2. Runtime: **Docker**. Dockerfile path: `api/Dockerfile`. Build context: repo root (`.`).
3. Health check: `/health`. Leave Docker Command blank.
4. Env: `GROQ_API_KEY`, `LLM_PROVIDER=groq`.
5. Prefer **Starter** over free if the free build OOMs.

First build can take 15–30 minutes (CPU torch + deps). If logs loop on `huggingface-hub … does not provide the extra 'inference'` with endless `ag2-0.x` downloads, cancel — that was the old loose `ag2` pin (fixed on `main`).

`railway.toml` still works for Railway if you prefer that (~$5 trial / paid after).

---

## 6. Troubleshooting

| Symptom | Fix |
|---------|-----|
| “API offline” on Vercel | Wrong/missing `NEXT_PUBLIC_API_URL`; redeploy Vercel |
| Mixed content / CORS | API must be **https://** |
| `groq: false` in `/health` | Fix `GROQ_API_KEY` in VM `.env`, recreate container |
| Docker build OOM on Oracle | Use 12 GB RAM shape or add swap |
| Demo times out | First run loads models — retry; check `docker compose logs` |

---

## Quick checklist

- [ ] `preflight --probe` passes locally
- [ ] Oracle VM: local `/health` OK
- [ ] Public HTTPS `/health` OK
- [ ] Vercel deployed with `NEXT_PUBLIC_API_URL`
- [ ] Chat + file demo tested live
- [ ] Portfolio `ai-lab.html` published
