#!/usr/bin/env bash
# Deploy sekolah-ai.my.id ke Cloudflare Pages.
#
# Alur: build Astro (di VPS, agar OG image via sharp siap) -> deploy via wrangler.
# Dipakai oleh cron auto_blogger (ganti auto-deploy Netlify).
#
# Token & account id dibaca dari ~/.config/openclaw/cloudflare.env
set -euo pipefail

REPO_DIR="/home/ubuntu/sekolah-ai.my.id"
ENV_FILE="$HOME/.config/openclaw/cloudflare.env"
PROJECT="sekolah-ai"

# --- Pastikan Node >= 22 (Astro 6 butuh >=22.12) --------------------------
# Cron menjalankan script ini dengan PATH minimal, sehingga bisa memakai
# /usr/bin/node (v20) yang TIDAK didukung Astro -> build gagal senyap.
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "$NVM_DIR/nvm.sh"
  nvm use 24 >/dev/null 2>&1 || nvm use --lts >/dev/null 2>&1 || true
fi
# Fallback: tambahkan versi nvm terbaru yang ada ke PATH
if ! node -v 2>/dev/null | grep -qE 'v(2[2-9]|[3-9][0-9])\.'; then
  LATEST_NVM_NODE="$(ls -d "$NVM_DIR"/versions/node/v* 2>/dev/null | sort -V | tail -1)"
  if [ -n "$LATEST_NVM_NODE" ]; then
    export PATH="$LATEST_NVM_NODE/bin:$PATH"
  fi
fi

NODE_VER="$(node -v 2>/dev/null || echo none)"
MAJOR="${NODE_VER#v}"; MAJOR="${MAJOR%%.*}"
if [ "${MAJOR:-0}" -lt 22 ]; then
  echo "❌ Node $NODE_VER tidak didukung (Astro butuh >=22.12). Perbaiki PATH/nvm."
  exit 1
fi
echo "🟢 Node $NODE_VER"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ $ENV_FILE tidak ada (butuh CLOUDFLARE_API_TOKEN & CLOUDFLARE_ACCOUNT_ID)"
  exit 1
fi
# shellcheck disable=SC1090
set -a; . "$ENV_FILE"; set +a

cd "$REPO_DIR"

# --- Build ke direktori bersih agar tidak ada stale dist -----------------
echo "🔨 Building..."
rm -rf dist
if ! npm run build >/tmp/cf-build.log 2>&1; then
  echo "❌ Build gagal — dist dikosongkan, deploy DIBATALKAN"
  tail -20 /tmp/cf-build.log
  exit 1
fi

# Sanity check: dist harus punya index.html
if [ ! -f dist/index.html ]; then
  echo "❌ dist/index.html tidak ada setelah build — deploy DIBATALKAN"
  tail -20 /tmp/cf-build.log
  exit 1
fi
echo "✅ Build OK ($(find dist -name '*.html' | wc -l) halaman)"

echo "🚀 Deploying to Cloudflare Pages..."
npx wrangler pages deploy dist \
  --project-name="$PROJECT" \
  --branch=main \
  --commit-dirty=true 2>&1 | tee /tmp/cf-deploy.log | tail -5

echo "🌐 https://sekolah-ai.my.id"
