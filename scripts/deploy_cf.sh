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

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ $ENV_FILE tidak ada (butuh CLOUDFLARE_API_TOKEN & CLOUDFLARE_ACCOUNT_ID)"
  exit 1
fi
# shellcheck disable=SC1090
set -a; . "$ENV_FILE"; set +a

cd "$REPO_DIR"

echo "🔨 Building..."
npm run build >/tmp/cf-build.log 2>&1 || { echo "❌ Build gagal"; tail -20 /tmp/cf-build.log; exit 1; }
echo "✅ Build OK"

echo "🚀 Deploying to Cloudflare Pages..."
npx wrangler pages deploy dist \
  --project-name="$PROJECT" \
  --branch=main \
  --commit-dirty=true 2>&1 | tee /tmp/cf-deploy.log | tail -5

echo "🌐 https://sekolah-ai.my.id"