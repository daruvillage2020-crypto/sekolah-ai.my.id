#!/usr/bin/env python3
"""
Auto Blogger for sekolah-ai.my.id - Gemini Edition (robust)
Output plain markdown, no JSON parsing issues.
"""

import os
import re
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

# Pool foto Unsplash per kategori (natural/real photos).
# Dipilih acak per artikel, dan dihindari duplikat dgn artikel yang sudah ada.
PHOTO_POOLS = {
    "ai": [
        "photo-1677442136019-21780ecad995",
        "photo-1620712943543-bcc4688e7485",
        "photo-1555255707-c07966088b7b",
        "photo-1526374965328-7f61d4dc18c5",
        "photo-1451187580459-43490279c0fa",
        "photo-1518770660439-4636190af475",
    ],
    "coding": [
        "photo-1461749280684-dccba630e2f6",
        "photo-1498050108023-c5249f4df085",
        "photo-1517694712202-14dd9538aa97",
        "photo-1555066931-4365d14bab8c",
        "photo-1542831371-29b0f74f9713",
        "photo-1504639725590-34d0984388bd",
        "photo-1526379095098-d400fd0bf935",
    ],
    "laptop": [
        "photo-1496181133206-80ce9b88a853",
        "photo-1517430816045-df4b7de11d1d",
        "photo-1531297484001-80022131f5a1",
        "photo-1587620962725-abab7fe55159",
    ],
    "security": [
        "photo-1563013544-824ae1b704d3",
        "photo-1563986768609-322da13575f3",
        "photo-1614064641938-3bbee52942c7",
        "photo-1550751827-4bd374c3f58b",
        "photo-1633265486064-086b219458ec",
    ],
    "school": [
        "photo-1562774053-701939374585",
        "photo-1580582932707-520aed937b7b",
        "photo-1503676260728-1c00da094a0b",
        "photo-1541339907198-e08756dedf3f",
        "photo-1546410531-bb4caa6b424d",
        "photo-1509062522246-3755977927d7",
    ],
    "education": [
        "photo-1524178232363-1fb2b075b655",
        "photo-1522071820081-009f0129c71c",
        "photo-1521737604893-d14cc237f11d",
        "photo-1600880292203-757bb62b4baf",
        "photo-1516321318423-f06f85e504b3",
        "photo-1517245386807-bb43f82c33c4",
    ],
    "data": [
        "photo-1551288049-bebda4e38f71",
        "photo-1531482615713-2afd69097998",
        "photo-1553877522-43269d4ea984",
        "photo-1552581234-26160f608093",
        "photo-1519389950473-47ba0277781c",
    ],
    "tech": [
        "photo-1499750310107-5fef28a66643",
        "photo-1486312338219-ce68d2c6f44d",
        "photo-1573164713988-8665fc963095",
    ],
}


def _categorize(title: str) -> str:
    """Map article title to a photo category."""
    t = title.lower()
    # word-boundary match utk keyword pendek biar tdk salah cocok (mis. "ai" dlm "wajib")
    words = re.findall(r"[a-z0-9]+", t)
    wset = set(words)

    if ("ai" in wset) or any(k in t for k in ["kecerdasan buatan", "neural", "machine learning", "deep learning", "robot", "chatbot", "computer vision"]):
        return "ai"
    if "laptop" in wset or "laptop" in t:
        return "laptop"
    if any(k in t for k in ["password", "keamanan", "security", "bobol", "privasi", "hacking", "cyber"]):
        return "security"
    if any(k in t for k in ["website sekolah", "gerbang pendidikan"]):
        return "school"
    if any(k in t for k in ["coding", "programming", "developer", "programmer", "koding"]):
        return "coding"
    if any(k in t for k in ["data", "analisis", "analytics", "data science"]):
        return "data"
    if any(k in t for k in ["belajar", "guru", "siswa", "modul ajar", "pendidikan", "pelajar", "sekolah", "kelas", "kuliah"]):
        return "education"
    return "tech"


def _used_covers() -> set:
    """Collect cover URLs already used by existing articles."""
    used = set()
    if CONTENT_DIR.exists():
        for f in CONTENT_DIR.glob("*.md"):
            for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("cover:"):
                    used.add(line.split("cover:", 1)[1].strip())
    return used


def pick_cover_image(title: str) -> str:
    """Pick a random, natural Unsplash cover for the article.

    Chooses a photo pool by topic category, then picks randomly while
    avoiding images already used by existing articles. Falls back to any
    photo in the pool (or picsum) if the pool is exhausted.
    """
    cat = _categorize(title)
    pool = PHOTO_POOLS.get(cat, PHOTO_POOLS["tech"])
    used = _used_covers()

    def to_url(pid: str) -> str:
        return f"https://images.unsplash.com/{pid}?w=1200&q=80"

    available = [p for p in pool if to_url(p) not in used]
    if not available:
        # Pool kategori habis -> fallback ke picsum unik per-judul (dijamin beda).
        seed = hashlib.md5(title.encode("utf-8")).hexdigest()[:12]
        return f"https://picsum.photos/seed/sekolahai-{seed}/1200/630"

    chosen = random.choice(available)
    return to_url(chosen)
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

    # Pick Unsplash cover image
    cover_url = pick_cover_image(title)
    
    frontmatter = f"---\ntitle: \"{title}\"\ndescription: \"{description}\"\ncover: {cover_url}\ndate: {date_iso}\nauthor: {author}\n---\n\n"
    filepath.write_text(frontmatter + content, encoding="utf-8")
    print(f"  💾 Saved: {filepath.name}")
    return filepath


def gen_og_images():
    """Generate OG share images for any new articles (idempotent)."""
    script = REPO_DIR / "scripts" / "gen-og.mjs"
    if not script.exists():
        return
    print("  🖼️  Generate OG images...", end=" ", flush=True)
    try:
        r = subprocess.run(
            ["node", str(script)],
            cwd=str(REPO_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode == 0:
            print("✅")
        else:
            print(f"⚠️  {r.stderr[:150]}")
    except Exception as e:
        print(f"⚠️  {e}")


def auto_social_post(title: str, slug: str, description: str):
    """Broadcast new article to configured social channels (skips if no token)."""
    script = REPO_DIR / "auto_social.py"
    if not script.exists():
        return
    url = f"https://sekolah-ai.my.id/blog/{slug}/"
    try:
        r = subprocess.run(
            ["python3", str(script), "--title", title, "--url", url, "--desc", description],
            cwd=str(REPO_DIR), capture_output=True, text=True, timeout=120,
        )
        out = (r.stdout or "").strip().splitlines()
        print("  " + (out[-1] if out else "📣 Auto-post: -(tidak ada output)"))
    except Exception as e:
        print(f"  ⚠️  Auto-post gagal: {e}")


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
    published = []
    for i, topic in enumerate(topics[: args.count]):
        print(f"\n[{i+1}/{args.count}] 📝 Topic: {topic}")
        try:
            article = generate_article(topic)
            if article:
                path = save_article(article, args.author)
                published.append((article["title"], path.stem, article["description"]))
                successful += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n{'='*60}")
    if successful > 0:
        print(f"  ✅ {successful} artikel sukses!")
        gen_og_images()
        if not args.no_push:
            git_push()
            for t, s, d in published:
                auto_social_post(t, s, d)
            print("  🌐 Netlify auto-deploy dalam ~2 menit")
    else:
        print("  ❌ Gagal, cek error di atas")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
