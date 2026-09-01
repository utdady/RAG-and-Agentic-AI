# AI Lab live demo hub

Next.js (Beautiful UI-inspired shell) for live demos. Backend: `../api`.

## Local

**Easiest:** from repo root run `.\scripts\start_lab.ps1` (starts API + UI in two windows).

Or manually:

```powershell
cd web
npm install
npm run dev:hub
```

Local dev uses the same-origin proxy at `/api/hub` — you do **not** need `NEXT_PUBLIC_API_URL` unless overriding production behavior.

Vercel: set **Root Directory** to `web`. Add `NEXT_PUBLIC_API_URL` pointing at your HTTPS API (Oracle VM). See [`../DEPLOY.md`](../DEPLOY.md) and [`../docs/deploy/oracle.md`](../docs/deploy/oracle.md).

Components: pixel loading state, thinking traces, task rows, tool chips, context cards, streaming text, prompt bar — mapped from the hub SSE contract in `../api/events.py`.
