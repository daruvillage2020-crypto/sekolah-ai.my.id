#!/usr/bin/env python3
"""
Tambah/update agenda (event) Sekolah AI dengan mudah.

Contoh:
  python3 scripts/add_event.py --title "Webinar AI untuk Guru" \
      --type webinar --start 2026-12-01 --time "19:30 - 21:00 WIB" \
      --mode online --price "Gratis" --desc "Deskripsi singkat kegiatan." \
      --reg "https://sekolah-ai.my.id/kontak" --speaker "Tim Sekolah AI"

Kalau slug sudah ada, file ditimpa (update). Tanpa --push, tidak commit.
Pakai --body-file untuk isi markdown detail dari file.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVENTS = REPO / "src/content/events"

TYPES = ["workshop", "bootcamp", "webinar", "meetup", "pelatihan", "lainnya"]
MODES = ["online", "offline", "hybrid"]


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return re.sub(r"-+", "-", s)[:80]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--desc", required=True, help="Deskripsi singkat (1-2 kalimat)")
    ap.add_argument("--type", default="lainnya", choices=TYPES)
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", help="YYYY-MM-DD (opsional, untuk multi-hari)")
    ap.add_argument("--time", help='mis. "09:00 - 15:00 WIB"')
    ap.add_argument("--mode", default="online", choices=MODES)
    ap.add_argument("--location", default="Zoom Meeting")
    ap.add_argument("--price", default="Gratis")
    ap.add_argument("--speaker")
    ap.add_argument("--reg", dest="registration_url", help="URL pendaftaran")
    ap.add_argument("--reg-note", dest="registration_note")
    ap.add_argument("--cover")
    ap.add_argument("--featured", action="store_true")
    ap.add_argument("--status", choices=["dibuka", "ditutup", "selesai"])
    ap.add_argument("--body-file", help="File markdown untuk isi detail")
    ap.add_argument("--slug", help="Slug custom (default: dari judul)")
    ap.add_argument("--push", action="store_true", help="git commit + push setelahnya")
    args = ap.parse_args()

    slug = args.slug or slugify(args.title)
    path = EVENTS / f"{slug}.md"

    body = ""
    if args.body_file:
        body = Path(args.body_file).read_text().strip()
    else:
        body = "## Tentang Kegiatan Ini\n\n_Tulis detail kegiatan di sini._\n"

    lines = [
        "---",
        f'title: "{args.title}"',
        f'description: "{args.desc}"',
        f"type: {args.type}",
        f"startDate: {args.start}",
    ]
    if args.end:
        lines.append(f"endDate: {args.end}")
    if args.time:
        lines.append(f'time: "{args.time}"')
    lines.append(f"mode: {args.mode}")
    lines.append(f'location: "{args.location}"')
    lines.append(f'price: "{args.price}"')
    if args.speaker:
        lines.append(f'speaker: "{args.speaker}"')
    if args.registration_url:
        lines.append(f'registrationUrl: "{args.registration_url}"')
    if args.registration_note:
        lines.append(f'registrationNote: "{args.registration_note}"')
    if args.cover:
        lines.append(f'cover: "{args.cover}"')
    if args.featured:
        lines.append("featured: true")
    if args.status:
        lines.append(f"statusOverride: {args.status}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    lines.append("")

    existed = path.exists()
    EVENTS.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"{'♻️  Updated' if existed else '✅ Created'}: src/content/events/{slug}.md")

    if args.push:
        subprocess.run(["git", "add", "-A"], cwd=REPO, check=True)
        msg = f"{'Update' if existed else 'Agenda'}: {args.title}"
        subprocess.run(["git", "commit", "-m", msg], cwd=REPO, check=True)
        r = subprocess.run(["git", "push"], cwd=REPO, capture_output=True, text=True)
        print("🚀 Push OK" if r.returncode == 0 else f"❌ {r.stderr[:200]}")
    else:
        print("ℹ️  Jalankan `npm run build` atau push manual untuk deploy.")


if __name__ == "__main__":
    sys.exit(main())