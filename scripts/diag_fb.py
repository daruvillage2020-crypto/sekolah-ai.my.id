#!/usr/bin/env python3
"""Diagnose system-user token: list pages, resolve alt id, try posting."""
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


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
ALT = env.get("FB_ALT_ID", "")

print("=== /me (system user) ===")
print(json.dumps(get(f"https://graph.facebook.com/v21.0/me?access_token={T}"), ensure_ascii=False)[:200])

print("\n=== /me/accounts ===")
accts = get(f"https://graph.facebook.com/v21.0/me/accounts?limit=200&access_token={T}")
for p in accts.get("data", []):
    print(f"  - {p['name']} | id={p['id']} | tasks={p.get('tasks')}")
if "__err" in accts:
    print("  ERR:", accts)

print(f"\n=== resolve ALT id {ALT} ===")
print(json.dumps(get(f"https://graph.facebook.com/v21.0/{ALT}?fields=id,name,username&access_token={T}"), ensure_ascii=False)[:300])

print("\n=== resolve FB_PAGE_ID 1201993219661703 ===")
print(json.dumps(get(f"https://graph.facebook.com/v21.0/1201993219661703?fields=id,name&access_token={T}"), ensure_ascii=False)[:300])

print("\n=== try post to ALT id ===")
for pid in [ALT, "1201993219661703"]:
    if not pid:
        continue
    req = urllib.request.Request(
        f"https://graph.facebook.com/v21.0/{pid}/feed",
        data=urllib.parse.urlencode(
            {"message": "Tes sistem Sekolah AI — mohon abaikan.", "access_token": T}
        ).encode(),
    )
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
        print(f"  {pid}: POST OK ->", r)
    except urllib.error.HTTPError as e:
        print(f"  {pid}: ERR {e.code}", e.read().decode()[:200])