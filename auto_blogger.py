#!/usr/bin/env python3
"""
Auto Blogger for sekolah-ai.my.id - Gemini Edition (robust)
Output plain markdown, no JSON parsing issues.
"""

import os
import sys
import hashlib
import random
import subprocess
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
import json

REPO_DIR = Path(os.path.expanduser("~/sekolah-ai.my.id"))
CONTENT_DIR = REPO_DIR / "src/content/blog"
COVERS_DIR = REPO_DIR / "public" / "images" / "blog"

# Gradient theme presets: (color1, color2, emoji)
COVER_THEMES = [
    ("#6a11cb", "#2575fc", "🤖"),  # AI / Tech
    ("#0f0c29", "#302b63", "💻"),  # Programming
    ("#1a1a2e", "#16213e", "🔒"),  # Security
    ("#0f2027", "#203a43", "🏫"),  # Education
    ("#00b4db", "#0083b0", "🌊"),  # Data/Blue
    ("#11998e", "#38ef7d", "🌿"),  # Growth/Green
    ("#fc4a1a", "#f7b733", "🔥"),  # Energy/Orange
    ("#834d9b", "#d04ed6", "✨"),  # Creative/Purple
]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

WIB = timezone(timedelta(hours=7))

TOPICS = [
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
    "cara menggunakan API AI untuk proyek sekolah",
    "AI untuk analisis data pendidikan",
    "membangun portfolio proyek AI",
    "cara domain .sch.id gratis untuk sekolah",
    "tips SEO untuk website sekolah",
    "cara membuat website sekolah gratis",
    "keamanan website untuk pemula",
    "cara hosting website sekolah murah",
    "optimasi gambar untuk website",
    "pentingnya website sekolah di era digital",
    "pengenalan data science untuk pemula",
    "cara menggunakan ChatGPT untuk belajar",
    "tips aman bersosial media untuk pelajar",
    "membangun aplikasi sederhana dengan AI",
    "cara membuat CV digital dengan AI",
]

def call_gemini(prompt: str) -> str:
    """Call Gemini API and return text response."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 8192,
        }
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(GEMINI_URL, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if "candidates" not in body or not body["candidates"]:
        if "promptFeedback" in body and body["promptFeedback"].get("blockReason"):
            raise Exception(f"Blocked: {body['promptFeedback']['blockReason']}")
        raise Exception(f"No candidates: {json.dumps(body)[:300]}")
    return body["candidates"][0]["content"]["parts"][0]["text"]


def generate_article(topic: str) -> dict:
    """Generate article title + description + content using Gemini (plain text)."""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set!")
        sys.exit(1)

    today = datetime.now(WIB)

    # Step 1: Generate title + description (plain text, delimiter-based)
    meta_prompt = f"""Buatlah judul artikel blog dan deskripsi singkat untuk topik berikut.

Topik: {topic}

Format output HARUS seperti ini (2 baris saja, tanpa tambahan lain):
JUDUL: <judul artikel yang menarik, maksimal 12 kata>
DESKRIPSI: <deskripsi 1-2 kalimat, maksimal 160 karakter>"""

    print(f"  🤖 [1/2] Buat judul + deskripsi...", end=" ", flush=True)
    meta_text = call_gemini(meta_prompt).strip()

    title = ""
    description = ""
    for line in meta_text.split("\n"):
        line = line.strip()
        if line.upper().startswith("JUDUL:"):
            title = line.split(":", 1)[1].strip()
        elif line.upper().startswith("DESKRIPSI:"):
            description = line.split(":", 1)[1].strip()

    if not title:
        # Fallback: gunakan topik sebagai judul
        title = " ".join(w.capitalize() for w in topic.split())
    if not description:
        description = f"Artikel tentang {topic} untuk pembaca Sekolah AI Indonesia."

    print(f"✅ '{title[:50]}'")

    # Step 2: Generate full content
    content_prompt = f"""Kamu adalah penulis blog profesional untuk website Sekolah AI Indonesia (sekolah-ai.my.id).

Tulis artikel blog lengkap dalam Bahasa Indonesia dengan judul: "{title}"

PERSYARATAN:
- Panjang: 800-1200 kata
- Gaya: informatif, praktis, mudah dipahami
- Struktur: 
  - Mulai langsung dengan paragraf Pendahuluan (tanpa heading "Pendahuluan" eksplisit)
  - Gunakan heading "## " untuk sub-bagian
  - Akhiri dengan paragraf Kesimpulan
- Sertakan tips, langkah praktis, atau contoh nyata
- Jangan gunakan emoji
- Format markdown standar (## untuk sub judul, daftar dengan - atau 1.)
- Jangan sertakan judul artikel di awal konten (judul sudah di frontmatter)

TULIS LANGSUNG KONTEN ARTIKELNYA (tanpa penjelasan apapun):"""

    print(f"  🤖 [2/2] Tulis konten artikel...", end=" ", flush=True)
    content = call_gemini(content_prompt).strip()
    print(f"✅ {len(content)} karakter")

    return {
        "title": title,
        "description": description[:160],
        "content": content,
    }


def generate_cover_svg(title: str, slug: str) -> str:
    """Generate aesthetic gradient SVG cover image for article."""
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    # Pick theme based on title hash
    idx = hashlib.md5(title.encode()).digest()[0] % len(COVER_THEMES)
    c1, c2, icon = COVER_THEMES[idx]

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="768" viewBox="0 0 1536 768">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c1};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{c2};stop-opacity:1" />
    </linearGradient>
    <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
      <path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
    </pattern>
    <filter id="glow">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="1536" height="768" fill="url(#bg)"/>
  <rect width="1536" height="768" fill="url(#grid)"/>
  <circle cx="200" cy="650" r="180" fill="rgba(255,255,255,0.04)"/>
  <circle cx="1400" cy="150" r="240" fill="rgba(255,255,255,0.03)"/>
  <circle cx="768" cy="100" r="100" fill="rgba(255,255,255,0.05)"/>
  <text x="120" y="420" font-size="200" filter="url(#glow)">{icon}</text>
  <circle cx="1100" cy="500" r="6" fill="rgba(255,255,255,0.3)"/>
  <circle cx="1130" cy="470" r="4" fill="rgba(255,255,255,0.2)"/>
  <circle cx="1160" cy="490" r="5" fill="rgba(255,255,255,0.25)"/>
  <circle cx="1280" cy="180" r="8" fill="rgba(255,255,255,0.15)"/>
  <circle cx="1320" cy="200" r="3" fill="rgba(255,255,255,0.2)"/>
</svg>'''

    svg_filename = f"cover-{slug}.svg"
    svg_path = COVERS_DIR / svg_filename
    svg_path.write_text(svg, encoding="utf-8")
    print(f"  🎨 Cover: /images/blog/{svg_filename}")
    return f"/images/blog/{svg_filename}"


def slugify(text: str) -> str:
    slug = text.lower().replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    return slug[:120]


def save_article(article: dict, author: str = "Tim Sekolah AI") -> Path:
    title = article["title"]
    description = article["description"][:160]
    content = article.get("content", "")
    now = datetime.now(WIB)
    slug = slugify(title)

    filepath = CONTENT_DIR / f"{slug}.md"
    if filepath.exists():
        suffix = hashlib.md5(title.encode()).hexdigest()[:6]
        filepath = CONTENT_DIR / f"{slug}-{suffix}.md"

    date_iso = now.strftime("%Y-%m-%dT%H:%M:%S.000+07:00")

    # Generate cover SVG
    cover_url = generate_cover_svg(title, slug)
    
    frontmatter = f"---\ntitle: \"{title}\"\ndescription: \"{description}\"\ncover: {cover_url}\ndate: {date_iso}\nauthor: {author}\n---\n\n"
    filepath.write_text(frontmatter + content, encoding="utf-8")
    print(f"  💾 Saved: {filepath.name}")
    return filepath


def git_push():
    print("  📤 Pushing to GitHub...", end=" ", flush=True)
    os.chdir(REPO_DIR)
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("⚠️  No changes")
        return
    subprocess.run(["git", "add", "-A"], capture_output=True)
    subprocess.run(["git", "commit", "-m", f"Auto-blog: {datetime.now(WIB).strftime('%d %B %Y %H:%M')}"], capture_output=True)
    result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
    print("✅ Push OK" if result.returncode == 0 else f"❌ {result.stderr[:200]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", "-c", type=int, default=1)
    parser.add_argument("--topic", "-t", type=str)
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--author", type=str, default="Tim Sekolah AI")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  🤖 SEkolah AI Auto Blogger")
    print(f"  📅 {datetime.now(WIB).strftime('%d %B %Y %H:%M %Z')}")
    print(f"  📂 {CONTENT_DIR}")
    print(f"{'='*60}\n")

    if not REPO_DIR.exists():
        print("❌ Repo tidak ditemukan")
        sys.exit(1)

    if args.topic:
        topics = [args.topic]
    else:
        topics = random.sample(TOPICS, min(args.count, len(TOPICS)))
    if len(topics) < args.count:
        remaining = [t for t in TOPICS if t not in topics]
        random.shuffle(remaining)
        topics.extend(remaining[: args.count - len(topics)])

    successful = 0
    for i, topic in enumerate(topics[: args.count]):
        print(f"\n[{i+1}/{args.count}] 📝 Topic: {topic}")
        try:
            article = generate_article(topic)
            if article:
                save_article(article, args.author)
                successful += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n{'='*60}")
    if successful > 0:
        print(f"  ✅ {successful} artikel sukses!")
        if not args.no_push:
            git_push()
            print("  🌐 Netlify auto-deploy dalam ~2 menit")
    else:
        print("  ❌ Gagal, cek error di atas")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
