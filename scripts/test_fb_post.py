#!/usr/bin/env python3
"""End-to-end test: post a real blog article to the Sekolah AI FB Page."""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("auto_social", "/home/ubuntu/sekolah-ai.my.id/auto_social.py")
m = importlib.util.module_from_spec(spec)
sys.argv = ["auto_social.py"]
spec.loader.exec_module(m)

import os

# Force dynamic path (no cached page token) to prove the system-user flow works.
os.environ.pop("FB_PAGE_ACCESS_TOKEN", None)
print("cached token removed -> testing dynamic fetch")
print("FB_PAGE_ID:", os.environ.get("FB_PAGE_ID"))
print("system token len:", len(os.environ.get("FB_PAGE_TOKEN", "")))

title = "Panduan Lengkap Kurikulum Merdeka: Strategi Praktis Guru Mengajar di Kelas"
url = "https://sekolah-ai.my.id/blog/panduan-lengkap-kurikulum-merdeka-strategi-praktis-guru-mengajar-di-kelas/"
desc = "Panduan praktis Kurikulum Merdeka untuk guru: strategi mengajar, asesmen, dan tips implementasi di kelas."

ok = m.post_facebook(title, url, desc)
print("RESULT:", "✅ BERHASIL" if ok else "❌ GAGAL")