#!/usr/bin/env bash
# Build and start the API container on the VM.
# Run from repo root: bash scripts/oracle/deploy-api.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [ ! -f .env ]; then
  echo "Missing .env — copy env.example and set GROQ_API_KEY:"
  echo "  cp env.example .env && nano .env"
  exit 1
fi

if ! grep -qE '^GROQ_API_KEY=.+$' .env; then
  echo "GROQ_API_KEY is empty in .env"
  exit 1
fi

echo "==> Building image (first run: 15–25 min on ARM)..."
docker compose build

echo "==> Starting API on 127.0.0.1:8080..."
docker compose up -d

echo "==> Waiting for /health..."
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1; then
    curl -s http://127.0.0.1:8080/health
    echo ""
    echo "API is up locally. Expose with HTTPS — see docs/deploy/oracle.md"
    exit 0
  fi
  sleep 5
done

echo "Health check timed out. Logs:"
docker compose logs --tail=80
exit 1
