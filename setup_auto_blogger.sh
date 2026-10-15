#!/usr/bin/env bash
# setup_auto_blogger.sh
# Run this script on your VPS to setup auto-blogger

set -e

REPO_URL="https://github.com/daruvillage2020-crypto/sekolah-ai.my.id.git"
REPO_DIR="$HOME/sekolah-ai.my.id"
SCRIPT_URL="https://raw.githubusercontent.com/daruvillage2020-crypto/sekolah-ai.my.id/main/auto_blogger.py"

echo "========================================"
echo "  SEkolah AI Auto Blogger Setup"
echo "========================================"
echo ""

# 1. Clone repo if not exists
if [ ! -d "$REPO_DIR" ]; then
    echo "[1/5] Cloning repository..."
    git clone "$REPO_URL" "$REPO_DIR"
else
    echo "[1/5] Repository already exists, pulling latest..."
    cd "$REPO_DIR" && git pull
fi

# 2. Check dependencies
echo "[2/5] Checking dependencies..."
if ! command -v python3 &>/dev/null; then
    echo "Installing python3..."
    sudo apt update && sudo apt install -y python3
fi
if ! command -v curl &>/dev/null; then
    echo "Installing curl..."
    sudo apt install -y curl
fi
if ! command -v git &>/dev/null; then
    echo "Installing git..."
    sudo apt install -y git
fi

# 3. Download the auto-blogger script
echo "[3/5] Downloading auto_blogger.py..."
# Copy from this repo or download
# Script should already be in the repo, but just in case:
if [ ! -f "$REPO_DIR/auto_blogger.py" ]; then
    # Will be placed manually later
    echo "  -> Place auto_blogger.py in $REPO_DIR/ manually"
fi

# 4. Setup cron job
echo "[4/5] Setting up cron job..."
# Check if cron already set
EXISTING_CRON=$(crontab -l 2>/dev/null || true)

# Every day at 08:00 and 20:00 WIB (00:00 and 12:00 UTC)
CRON_JOB_1="0 0 * * * cd $REPO_DIR && python3 auto_blogger.py --count 1 >> $HOME/auto_blogger.log 2>&1"
CRON_JOB_2="0 12 * * * cd $REPO_DIR && python3 auto_blogger.py --count 1 >> $HOME/auto_blogger.log 2>&1"

if echo "$EXISTING_CRON" | grep -q "auto_blogger"; then
    echo "  -> Cron job already exists, skipping"
else
    (echo "$EXISTING_CRON"; echo "$CRON_JOB_1"; echo "$CRON_JOB_2") | crontab -
    echo "  ✅ Cron jobs added!"
    echo "     - 08:00 WIB every day"
    echo "     - 20:00 WIB every day"
fi

# 5. Setup environment
echo "[5/5] Setup environment..."
if ! grep -q "OPENROUTER_API_KEY" "$HOME/.bashrc" 2>/dev/null; then
    echo ""
    echo "⚠️  OPENROUTER_API_KEY not found in .bashrc!"
    echo "   Add this to your ~/.bashrc or ~/.profile:"
    echo "   export OPENROUTER_API_KEY='sk-or-v1-YOUR_KEY_HERE'"
    echo ""
    echo "   Then run: source ~/.bashrc"
fi

echo ""
echo "========================================"
echo "  ✅ Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Set OPENROUTER_API_KEY in ~/.bashrc"
echo "2. Place auto_blogger.py in $REPO_DIR/"
echo "3. Run manually once: cd $REPO_DIR && python3 auto_blogger.py"
echo "4. Check logs: tail -f ~/auto_blogger.log"
echo ""
