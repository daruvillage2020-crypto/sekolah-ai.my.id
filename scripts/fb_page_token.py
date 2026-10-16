#!/usr/bin/env python3
"""Get the Page Access Token from /me/accounts and test a real post."""
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PAGE_ID = "1201993219661703"


def load_env():
    p = Path.home() / ".config/openclaw/social.env"
    out = {}
    for line in p.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def get(url):
    try:
        return json.loads(urllib.request.urlopen(url, timeout=30).read())
    except urllib.error.HTTPError as e:
        return {"__err": e.code, "body": e.read().decode()[:300]}


env = load_env()
T = env["FB_PAGE_TOKEN"]

accts = get(f"https://graph.facebook.com/v21.0/me/accounts?limit=200&access_token={T}")
page_token = None
for p in accts.get("data", []):
    if p["id"] == PAGE_ID:
        page_token = p.get("access_token")
print("page_token found:", bool(page_token), "| len:", len(page_token or ""))

if page_token:
    dbg = get(f"https://graph.facebook.com/v21.0/debug_token?input_token={page_token}&access_token={T}")
    print("page token scopes:", dbg.get("data", {}).get("scopes"))
    print("page token expires:", dbg.get("data", {}).get("expires_at"))

if page_token:
    # real post test
    req = urllib.request.Request(
        f"https://graph.facebook.com/v21.0/{PAGE_ID}/feed",
        data=urllib.parse.urlencode(
            {"message": "Tes sistem Sekolah AI — mohon abaikan.", "access_token": page_token}
        ).encode(),
    )
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
        print("POST OK:", r)
        POST_ID = r.get("id")
        # save page token + cleanup post
        with open(Path.home() / ".config/openclaw/social.env", "a") as f:
            f.write(f"FB_PAGE_ACCESS_TOKEN={page_token}\n")
        print("saved FB_PAGE_ACCESS_TOKEN")
        # delete test post
        d = get(f"https://graph.facebook.com/v21.0/{POST_ID}?method=delete&access_token={page_token}")
        print("cleanup:", d)
    except urllib.error.HTTPError as e:
        print("POST ERR", e.code, e.read().decode()[:300])