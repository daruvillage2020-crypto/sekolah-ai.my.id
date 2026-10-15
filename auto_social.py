#!/usr/bin/env python3
"""
Auto-post sosmed untuk sekolah-ai.my.id
Dijalankan otomatis oleh auto_blogger.py setiap habis publish artikel baru.

Token dibaca dari environment (JANGAN commit ke repo):
  TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID   -> Telegram channel/grup
  FB_PAGE_ID + FB_PAGE_TOKEN              -> Facebook Page
  LINKEDIN_TOKEN + LINKEDIN_AUTHOR_URN    -> LinkedIn
  X_API_KEY ... (opsional, X/Twitter)
  BLUESKY_HANDLE + BLUESKY_APP_PASSWORD   -> Bluesky

Kalau token tidak diset, channel itu dilewati (tanpa error).
"""

import os
import json
import argparse
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from pathlib import Path
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))
SITE = "https://www.sekolah-ai.my.id"


def post_telegram(title: str, url: str, desc: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return False
    text = f"📚 *{title}*\n\n{desc}\n\n👉 Baca: {url}"
    data = urlencode({"chat_id": chat, "text": text, "parse_mode": "Markdown"}).encode()
    req = Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
    try:
        with urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception as e:
        print(f"    ⚠️  Telegram gagal: {e}")
        return False


def post_facebook(title: str, url: str, desc: str) -> bool:
    page_id = os.environ.get("FB_PAGE_ID")
    token = os.environ.get("FB_PAGE_TOKEN")
    if not page_id or not token:
        return False
    msg = f"📚 {title}\n\n{desc}\n\nBaca selengkapnya: {url}"
    data = urlencode({"message": msg, "link": url, "access_token": token}).encode()
    req = Request(f"https://graph.facebook.com/v21.0/{page_id}/feed", data=data)
    try:
        with urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception as e:
        print(f"    ⚠️  Facebook gagal: {e}")
        return False


def post_linkedin(title: str, url: str, desc: str) -> bool:
    token = os.environ.get("LINKEDIN_TOKEN")
    author = os.environ.get("LINKEDIN_AUTHOR_URN")
    if not token or not author:
        return False
    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": f"📚 {title}\n\n{desc}"},
                "shareMediaCategory": "ARTICLE",
                "media": [{"status": "READY", "originalUrl": url}],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    req = Request(
        "https://api.linkedin.com/v2/ugcPosts",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    try:
        with urlopen(req, timeout=30) as r:
            return r.status in (200, 201)
    except Exception as e:
        print(f"    ⚠️  LinkedIn gagal: {e}")
        return False


def post_bluesky(title: str, url: str, desc: str) -> bool:
    handle = os.environ.get("BLUESKY_HANDLE")
    pw = os.environ.get("BLUESKY_APP_PASSWORD")
    if not handle or not pw:
        return False
    try:
        # login
        req = Request(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            data=json.dumps({"identifier": handle, "password": pw}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(req, timeout=30) as r:
            session = json.loads(r.read())
        text = f"📚 {title}\n\n{desc}\n\n{url}"
        payload = {
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": text[:300],
                "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "facets": [],
            },
        }
        req = Request(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {session['accessJwt']}",
                "Content-Type": "application/json",
            },
        )
        with urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception as e:
        print(f"    ⚠️  Bluesky gagal: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--desc", default="")
    args = ap.parse_args()

    results = {
        "telegram": post_telegram(args.title, args.url, args.desc),
        "facebook": post_facebook(args.title, args.url, args.desc),
        "linkedin": post_linkedin(args.title, args.url, args.desc),
        "bluesky": post_bluesky(args.title, args.url, args.desc),
    }
    active = [k for k, v in results.items() if v]
    if active:
        print(f"  📣 Auto-post OK: {', '.join(active)}")
    else:
        print("  📣 Auto-post: tidak ada channel aktif (token belum diset)")


if __name__ == "__main__":
    main()