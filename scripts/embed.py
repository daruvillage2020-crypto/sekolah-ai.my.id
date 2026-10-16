#!/usr/bin/env python3
"""
Backfill/update semantic embeddings untuk artikel blog sekolah-ai.my.id.

Menghitung embedding (via gateway OpenAI-compatible) untuk tiap artikel,
menyimpannya ke src/data/embeddings.json. Idempotent: artikel yang sudah
punya embedding & isinya tidak berubah akan dilewati.

Key diambil dari (urut prioritas):
  1. env SUMPOD_API_KEY / OPENAI_API_KEY
  2. ~/.config/openclaw/ai.env
  3. ~/.openclaw/openclaw.json (providers.custom-*)

Usage:
  python3 scripts/embed.py            # hanya artikel baru/berubah
  python3 scripts/embed.py --force    # hitung ulang semua
"""

import os
import sys
import json
import hashlib
import argparse
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "src/content/blog"
OUT = ROOT / "src/data/embeddings.json"

MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")
BASE = os.environ.get("EMBED_BASE_URL", "https://ai.sumopod.com/v1")


def load_key() -> str:
    for v in ("SUMPOD_API_KEY", "OPENAI_API_KEY", "EMBED_API_KEY"):
        if os.environ.get(v):
            return os.environ[v]
    envf = Path(os.path.expanduser("~/.config/openclaw/ai.env"))
    if envf.exists():
        for line in envf.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, val = line.split("=", 1)
                os.environ.setdefault(k.strip(), val.strip().strip('"').strip("'"))
        for v in ("SUMPOD_API_KEY", "OPENAI_API_KEY", "EMBED_API_KEY"):
            if os.environ.get(v):
                return os.environ[v]
    cfg = Path(os.path.expanduser("~/.openclaw/openclaw.json"))
    if cfg.exists():
        try:
            d = json.loads(cfg.read_text())
            provs = (d.get("models", {}) or {}).get("providers", {}) or d.get("providers", {})
            for p in provs.values():
                if isinstance(p, dict) and p.get("apiKey"):
                    return p["apiKey"]
        except Exception:
            pass
    return ""


def read_post(path: Path):
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---")
    fm = parts[1] if len(parts) >= 3 else ""
    body = "---".join(parts[2:]) if len(parts) >= 3 else raw

    def field(name):
        for line in fm.splitlines():
            if line.strip().lower().startswith(name + ":"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")
        return ""

    title = field("title") or path.stem
    desc = field("description")
    # teks untuk embedding: judul (dibobot) + deskripsi + isi (dipotong)
    text = f"{title}\n{title}\n{desc}\n{body[:6000]}"
    return title, desc, text


def embed(key: str, text: str):
    payload = json.dumps({"model": MODEL, "input": text}).encode()
    req = urllib.request.Request(
        f"{BASE}/embeddings",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    return d["data"][0]["embedding"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("❌ Tidak ada API key embedding (set SUMPOD_API_KEY). Skip.")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    store = {}
    if OUT.exists():
        try:
            store = json.loads(OUT.read_text())
        except Exception:
            store = {}

    files = sorted(BLOG.glob("*.md"))
    made = skipped = failed = 0
    for f in files:
        slug = f.stem
        _, _, text = read_post(f)
        h = hashlib.sha256(text.encode()).hexdigest()[:16]
        entry = store.get(slug)
        if not args.force and entry and entry.get("hash") == h and entry.get("vector"):
            skipped += 1
            continue
        try:
            vec = embed(key, text)
            store[slug] = {"hash": h, "model": MODEL, "vector": vec}
            made += 1
            print(f"  🧠 {slug}  ({len(vec)}d)")
        except Exception as e:
            failed += 1
            print(f"  ⚠️  {slug}: {e}")

    OUT.write_text(json.dumps(store, ensure_ascii=False))
    print(f"Embeddings: {made} dibuat, {skipped} dilewati, {failed} gagal → {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())