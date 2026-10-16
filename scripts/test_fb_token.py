#!/usr/bin/env python3
"""Test FB page token: debug scopes + try posting. Reads token from argv/stdin file."""
import json
import sys
import time
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


def main():
    env = load_env()
    T = env.get("FB_PAGE_TOKEN", "")
    P = env.get("FB_PAGE_ID", "")
    print("token len:", len(T), "| page:", P)

    dbg = get(f"https://graph.facebook.com/v21.0/debug_token?input_token={T}&access_token={T}")
    d = dbg.get("data", dbg)
    print("valid:", d.get("is_valid"), "| type:", d.get("type"))
    print("scopes:", d.get("scopes"))
    if d.get("expires_at"):
        print("expires:", time.strftime("%Y-%m-%d %H:%M", time.localtime(d["expires_at"])))
    else:
        print("expires: NEVER (system user) OK")

    pt = get(f"https://graph.facebook.com/v21.0/{P}?fields=access_token&access_token={T}")
    page_token = pt.get("access_token")
    print("page token ok:", bool(page_token))
    if not page_token:
        print("ERR:", json.dumps(pt)[:200])
        return 1

    pt_dbg = get(f"https://graph.facebook.com/v21.0/debug_token?input_token={page_token}&access_token={page_token}")
    print("page token scopes:", pt_dbg.get("data", {}).get("scopes"))

    req = urllib.request.Request(
        f"https://graph.facebook.com/v21.0/{P}/feed",
        data=urllib.parse.urlencode(
            {"message": "Tes sistem Sekolah AI — mohon abaikan.", "access_token": page_token}
        ).encode(),
    )
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
        print("POST OK:", r)
        return 0
    except urllib.error.HTTPError as e:
        print("POST ERR", e.code, e.read().decode()[:250])
        return 1


if __name__ == "__main__":
    sys.exit(main())