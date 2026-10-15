#!/usr/bin/env python3
"""
Auto Blogger for sekolah-ai.my.id
- Generate articles using OpenRouter AI API
- Save as .md to src/content/blog/
- Git commit & push → triggers Netlify deployment

Usage:
  ./auto_blogger.py              # generate 1 random article
  ./auto_blogger.py --count 3   # generate 3 articles
  ./auto_blogger.py --topic "tips belajar AI"  # specific topic
"""

import os
import sys
import json
import hashlib
import random
import subprocess
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─────────────────────── CONFIG ───────────────────────

REPO_DIR = Path(os.path.expanduser("~/sekolah-ai.my.id"))
CONTENT_DIR = REPO_DIR / "src/content/blog"

# OpenRouter API
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = "openai/gpt-4o-mini"  # cheap & fast, change if needed

WIB = timezone(timedelta(hours=7))

# ─────────────────── TOPIC GENERATOR ───────────────────

TOPICS = [
    # Pendidikan
    "cara membuat modul ajar dengan AI",
    "tips belajar efektif untuk siswa",
    "manfaat AI dalam dunia pendidikan",
    "peran guru di era kecerdasan buatan",
    "strategi pembelajaran diferensiasi",
    "cara mendeteksi plagiarism dengan AI",
    "aplikasi AI untuk membantu tugas sekolah",
    "belajar coding untuk pemula",
    "tips memilih jurusan kuliah",
    "pentingnya literasi digital untuk siswa",
    "cara membuat presentasi menarik dengan AI",
    "panduan kurikulum merdeka untuk guru",
    "rekomendasi tools AI gratis untuk guru",
    "cara mengelola kelas online",
    "tips meningkatkan konsentrasi belajar",

    # Teknologi / AI
    "apa itu machine learning dan contohnya",
    "perbedaan AI, ML, dan deep learning",
    "pengenalan neural network untuk pemula",
    "cara AI bekerja dalam kehidupan sehari-hari",
    "aplikasi AI di bidang kesehatan",
    "etika penggunaan AI",
    "masa depan AI dan dampaknya pada pekerjaan",
    "rekomendasi kursus AI online gratis",
    "cara membuat chatbot sederhana",
    "pengenalan computer vision",
    "belajar prompt engineering untuk pemula",
    "perbandingan GPT, Claude, dan Gemini",
    "cara menggunakan API AI untuk proyek sekolah",
    "AI untuk analisis data pendidikan",
    "membangun portfolio proyek AI",

    # Website & Digital
    "cara domain .sch.id gratis untuk sekolah",
    "tips SEO untuk website sekolah",
    "cara membuat website sekolah gratis",
    "keamanan website untuk pemula",
    "cara hosting website sekolah murah",
    "optimasi gambar untuk website",
    "pentingnya website sekolah di era digital",
]

# ─────────────────── GENERATE ARTICLE ───────────────────

def generate_article(topic: str) -> dict:
    """Generate an article using OpenRouter API."""
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not set!")
        print("   export OPENROUTER_API_KEY='sk-or-v1-...'")
        sys.exit(1)

    today = datetime.now(WIB)
    date_str = today.strftime("%Y-%m-%dT%H:%M:%S.000+07:00")
    
    system_prompt = """Kamu adalah penulis blog tentang AI, teknologi, dan pendidikan untuk website Sekolah AI Indonesia.

Tugasmu:
1. Buat artikel blog dalam Bahasa Indonesia yang natural dan engaging
2. Panjang: 800-1200 kata
3. Gaya: informatif, praktis, mudah dipahami
4. Struktur: judul menarik, pendahuluan, sub-topik (gunakan ##), kesimpulan
5. Sertakan tips atau langkah praktis
6. Jangan gunakan emoji berlebihan

OUTPUT FORMAT (hanya output JSON ini, tanpa teks lain):
{
  "title": "Judul Artikel",
  "description": "Deskripsi singkat 1-2 kalimat",
  "content": "Markdown content dari artikel lengkap"
}"""

    user_prompt = f"Buat artikel blog dengan topik: {topic}. Tanggal hari ini: {today.strftime('%d %B %Y')}"

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 4096,
    }

    print(f"  🤖 Generating with {OPENROUTER_MODEL}...", end=" ", flush=True)
    
    result = subprocess.run(
        [
            "curl", "-s", "-w", "\\n%{http_code}",
            "https://openrouter.ai/api/v1/chat/completions",
            "-H", f"Authorization: Bearer {OPENROUTER_API_KEY}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
        ],
        capture_output=True, text=True, timeout=120,
    )

    lines = result.stdout.strip().split("\n")
    http_code = lines[-1]
    body = "\n".join(lines[:-1])

    if http_code != "200":
        print(f"❌ HTTP {http_code}")
        print(body[:500])
        return None

    try:
        data = json.loads(body)
        raw = data["choices"][0]["message"]["content"]
        # Clean up markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        article = json.loads(raw)
        print(f"✅ '{article['title'][:50]}...'")
        return article
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Parse error: {e}")
        print(body[:500])
        return None


# ─────────────────── SAVE ARTICLE ───────────────────

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    slug = text.lower()
    slug = slug.replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    slug = slug.strip("-")
    # Truncate to avoid overly long filenames
    return slug[:120]


def save_article(article: dict, author: str = "Tim Sekolah AI") -> Path:
    """Save article as .md file."""
    title = article["title"]
    description = article["description"]
    content = article.get("content", "")

    now = datetime.now(WIB)
    slug = slugify(title)
    
    # Add suffix if slug already exists
    filepath = CONTENT_DIR / f"{slug}.md"
    if filepath.exists():
        suffix = hashlib.md5(title.encode()).hexdigest()[:6]
        slug = f"{slug}-{suffix}"
        filepath = CONTENT_DIR / f"{slug}.md"

    date_iso = now.strftime("%Y-%m-%dT%H:%M:%S.000+07:00")

    frontmatter = f"""---
title: {title}
description: {description}
date: {date_iso}
author: {author}
---

"""

    filepath.write_text(frontmatter + content, encoding="utf-8")
    print(f"  💾 Saved: {filepath.name}")
    return filepath


# ─────────────────── GIT PUSH ───────────────────

def git_push():
    """Commit and push changes to trigger Netlify deploy."""
    print("  📤 Pushing to GitHub...", end=" ", flush=True)
    
    os.chdir(REPO_DIR)
    
    # Check if there are changes
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("⚠️  No changes to commit")
        return

    subprocess.run(["git", "add", "-A"], capture_output=True)
    subprocess.run(["git", "commit", "-m", f"Auto-blog: {datetime.now(WIB).strftime('%d %B %Y %H:%M')}"], capture_output=True)
    result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        print(f"✅ Push OK")
    else:
        print(f"❌ Push failed: {result.stderr[:300]}")


# ─────────────────── MAIN ───────────────────

def main():
    parser = argparse.ArgumentParser(description="Auto Blogger for sekolah-ai.my.id")
    parser.add_argument("--count", "-c", type=int, default=1, help="Number of articles to generate")
    parser.add_argument("--topic", "-t", type=str, help="Specific topic (otherwise random)")
    parser.add_argument("--no-push", action="store_true", help="Don't push to GitHub")
    parser.add_argument("--author", type=str, default="Tim Sekolah AI", help="Article author")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  🤖 SEkolah AI Auto Blogger")
    print(f"  📅 {datetime.now(WIB).strftime('%d %B %Y %H:%M %Z')}")
    print(f"  📂 {CONTENT_DIR}")
    print(f"{'='*60}\n")

    # Ensure repo exists
    if not REPO_DIR.exists():
        print(f"❌ Repo dir {REPO_DIR} not found!")
        print("   Clone it first: git clone <repo-url> ~/sekolah-ai.my.id")
        sys.exit(1)

    topics = []
    if args.topic:
        topics = [args.topic]
    else:
        topics = random.sample(TOPICS, min(args.count, len(TOPICS)))

    # Pick unique topics
    if len(topics) < args.count:
        # Add more from shuffled pool
        remaining = [t for t in TOPICS if t not in topics]
        random.shuffle(remaining)
        topics.extend(remaining[: args.count - len(topics)])

    successful = 0
    for i, topic in enumerate(topics[: args.count]):
        print(f"\n[{i+1}/{args.count}] 📝 Topic: {topic}")
        article = generate_article(topic)
        if article:
            save_article(article, args.author)
            successful += 1

    print(f"\n{'='*60}")
    if successful > 0:
        print(f"  ✅ {successful} article(s) generated successfully!")
        if not args.no_push:
            git_push()
            print(f"  🌐 Netlify will deploy automatically in ~2 minutes")
        else:
            print(f"  ⏭️  Git push skipped (--no-push)")
    else:
        print(f"  ❌ No articles generated, check errors above")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
