#!/usr/bin/env bash
# Oracle Cloud Ubuntu VM — one-time setup.
# Run as your normal user (not root). Uses sudo where needed.
#
#   curl -fsSL https://raw.githubusercontent.com/utdady/RAG-and-Agentic-AI/main/scripts/oracle/setup-vm.sh | bash
# Or after cloning:
#   bash scripts/oracle/setup-vm.sh

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/utdady/RAG-and-Agentic-AI.git}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/RAG-and-Agentic-AI}"

echo "==> Installing Docker (if missing)..."
if ! command -v docker >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl gnupg
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER"
  echo "Added $USER to docker group — log out and back in if docker permission denied."
fi

echo "==> Cloning repo to $INSTALL_DIR..."
if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

if [ ! -f .env ]; then
  cp env.example .env
  echo ""
  echo "Created $INSTALL_DIR/.env — edit it and set GROQ_API_KEY before starting:"
  echo "  nano $INSTALL_DIR/.env"
  echo ""
fi

echo "==> Opening host firewall for HTTP/HTTPS (Oracle iptables)..."
if command -v iptables >/dev/null 2>&1; then
  sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
  sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT 2>/dev/null || true
  if command -v netfilter-persistent >/dev/null 2>&1; then
    sudo netfilter-persistent save 2>/dev/null || true
  fi
fi

echo ""
echo "Setup done. Next steps:"
echo "  1. nano $INSTALL_DIR/.env   # set GROQ_API_KEY, LLM_PROVIDER=groq"
echo "  2. bash $INSTALL_DIR/scripts/oracle/deploy-api.sh"
echo "  3. Follow docs/deploy/oracle.md for HTTPS (nginx + certbot or Cloudflare Tunnel)"
