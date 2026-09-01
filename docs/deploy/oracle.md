# Deploy API on Oracle Cloud (Always Free)

Host the FastAPI backend on an **Ampere A1** VM ($0/month) and pair it with **Vercel** (free) for the UI.

```
Portfolio (GitHub Pages)     Vercel (web/)           Oracle VM (api/)
utdady.github.io      →    lab.vercel.app     →    https://api.yourdomain.com
```

**Why Oracle?** Always Free tier gives up to **4 OCPU / 24 GB RAM** (ARM) — enough for torch, Chroma, and embeddings. No 30-day credit cliff like Railway.

**HTTPS is required.** Vercel is `https://`; the browser blocks calls to `http://` APIs (mixed content). Use nginx + Let's Encrypt (best) or Cloudflare Tunnel (quick test).

---

## Part A — Create the VM (Oracle Console)

### 1. Sign up

1. [cloud.oracle.com](https://www.oracle.com/cloud/free/) → create account (card may be required; Always Free resources stay $0).
2. Pick a **home region** close to you — **cannot change later**.

### 2. Create a compute instance

**Compute → Instances → Create instance**

| Setting | Value |
|---------|--------|
| Name | `ai-lab-api` |
| Image | **Ubuntu 22.04** or **24.04** (aarch64) |
| Shape | **Ampere** → `VM.Standard.A1.Flex` |
| OCPUs | **2** |
| Memory | **12 GB** |
| Boot volume | 50–100 GB |
| SSH key | Upload your public key (generate with `ssh-keygen` if needed) |

Click **Create**. Note the **public IP** when it’s running.

### 3. Open network ports

**Networking → Virtual cloud networks → your VCN → Security Lists → Default**

Add **Ingress** rules:

| Source | Protocol | Port | Description |
|--------|----------|------|-------------|
| `0.0.0.0/0` | TCP | 22 | SSH |
| `0.0.0.0/0` | TCP | 80 | HTTP (certbot + redirect) |
| `0.0.0.0/0` | TCP | 443 | HTTPS |

Save. The setup script also opens local iptables rules (Oracle images often need both).

### 4. SSH in

```powershell
ssh -i C:\Users\YOU\.ssh\id_ed25519 ubuntu@YOUR_PUBLIC_IP
```

---

## Part B — Install API on the VM

### 5. Run setup script

On the VM:

```bash
git clone https://github.com/utdady/RAG-and-Agentic-AI.git
cd RAG-and-Agentic-AI
bash scripts/oracle/setup-vm.sh
```

If you were added to the `docker` group, log out and SSH back in.

### 6. Configure secrets

```bash
nano ~/RAG-and-Agentic-AI/.env
```

Set at minimum:

```env
GROQ_API_KEY=gsk_your_key_here
LLM_PROVIDER=groq
```

### 7. Build and start

```bash
cd ~/RAG-and-Agentic-AI
bash scripts/oracle/deploy-api.sh
```

First Docker build on ARM takes **15–25 minutes**. When done:

```bash
curl http://127.0.0.1:8080/health
```

Expect `"ok": true` and `"groq": true`.

---

## Part C — HTTPS (pick one)

### Option 1 — nginx + Let's Encrypt (recommended for portfolio)

You need a domain (or subdomain) pointing at the VM’s public IP, e.g. `api.lab.yourdomain.com` → A record → `YOUR_PUBLIC_IP`.

On the VM:

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx

sudo cp ~/RAG-and-Agentic-AI/scripts/oracle/nginx-ai-lab-api.conf /etc/nginx/sites-available/ai-lab-api
sudo sed -i 's/API_DOMAIN/api.lab.yourdomain.com/g' /etc/nginx/sites-available/ai-lab-api
sudo ln -sf /etc/nginx/sites-available/ai-lab-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

sudo certbot --nginx -d api.lab.yourdomain.com
```

Verify:

```bash
curl https://api.lab.yourdomain.com/health
```

Use this URL as `NEXT_PUBLIC_API_URL` on Vercel.

### Option 2 — Cloudflare Tunnel (quick test, no domain)

Good for validating Vercel ↔ API before DNS is ready.

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
./cloudflared tunnel --url http://127.0.0.1:8080
```

Copy the `https://….trycloudflare.com` URL. Set that as `NEXT_PUBLIC_API_URL` on Vercel.

**Note:** Quick Tunnel URLs change when you restart `cloudflared`. Use Option 1 for anything permanent.

---

## Part D — Vercel (UI)

1. [vercel.com](https://vercel.com) → import `RAG-and-Agentic-AI`.
2. **Root Directory:** `web`
3. Environment variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://api.lab.yourdomain.com` (or Cloudflare tunnel URL) |
| `NEXT_PUBLIC_PORTFOLIO_URL` | `https://utdady.github.io` |

4. Deploy → open **Math Assistant** → confirm streaming works.

---

## Part E — Portfolio

1. Copy `docs/portfolio/ai-lab.html` → your `utdady.github.io` repo.
2. Set `LIVE_HUB_URL` to your Vercel URL.
3. Add nav link: `<a href="/ai-lab.html">AI Lab</a>`.

---

## Day-2 operations

### Update after git push

```bash
cd ~/RAG-and-Agentic-AI
git pull
bash scripts/oracle/deploy-api.sh
```

### View logs

```bash
cd ~/RAG-and-Agentic-AI
docker compose logs -f
```

### Restart

```bash
docker compose restart
```

### Optional API keys (extra demos)

Add to `.env` on the VM, then `docker compose up -d --force-recreate`:

| Variable | Demos |
|----------|-------|
| `SERPER_API_KEY` | CrewAI web search |
| `TAVILY_API_KEY` | LangGraph search |
| `GOOGLE_API_KEY` | Image generation |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Can't SSH | Check security list port 22; confirm public IP |
| `docker: permission denied` | `sudo usermod -aG docker $USER`, re-login |
| Build OOM | Use 12 GB RAM shape; add swap: `sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile` |
| Port 80/443 unreachable | OCI security list **and** VM iptables (setup script handles iptables) |
| Vercel “API offline” | `NEXT_PUBLIC_API_URL` must be **https**; test `/health` in browser |
| Mixed content error | API is still HTTP — finish certbot or use Cloudflare Tunnel |
| `groq: false` | Fix `GROQ_API_KEY` in `.env`, run `docker compose up -d --force-recreate` |
| Slow first demo | Cold embedding load — normal; retry |

---

## Checklist

- [ ] Ampere A1 VM running (2 OCPU / 12 GB)
- [ ] Ports 22, 80, 443 open in OCI security list
- [ ] `curl http://127.0.0.1:8080/health` OK on VM
- [ ] HTTPS URL works (`curl https://your-api/health`)
- [ ] Vercel deployed with `NEXT_PUBLIC_API_URL`
- [ ] Live demo streams on Vercel
- [ ] Portfolio `ai-lab.html` links to Vercel hub

---

## Cost summary

| Service | Cost |
|---------|------|
| Oracle Ampere A1 (within free limits) | **$0/mo** |
| Vercel hobby | **$0/mo** |
| GitHub Pages portfolio | **$0/mo** |
| Groq inference | Free tier / pay per use |
| Domain (optional) | ~$10–15/yr |
