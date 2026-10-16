#!/usr/bin/env python3
"""Update AI_MODEL env var on Netlify for sekolah-ai site."""
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

NEW_MODEL = "deepseek-v4.1-flash:netra"

tok = [
    l.split("=", 1)[1].strip().strip('"').strip("'")
    for l in (Path.home() / ".config/openclaw/netlify.env").read_text().splitlines()
    if l.startswith("NETLIFY_TOKEN=")
][0]

acct = "6a2f2dad1463d6caa5b32402"
site = "bae9e1cc-2afb-4344-920f-9d51cb6abf56"

# Try single-key update endpoint first, else fall back to bulk POST.
url1 = f"https://api.netlify.com/api/v1/accounts/{acct}/env/AI_MODEL?site_id={site}"
for method in ("PUT", "PATCH"):
    req = urllib.request.Request(
        url1,
        data=json.dumps({"value": NEW_MODEL}).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        r = urllib.request.urlopen(req, timeout=30)
        d = json.loads(r.read())
        print(f"OK {method} {r.status}: {d.get('key')} = {NEW_MODEL}")
        raise SystemExit(0)
    except urllib.error.HTTPError as e:
        print(f"  {method} HTTP {e.code}: {e.read()[:200]}")
    except SystemExit:
        raise
    except Exception as e:
        print(f"  {method} err: {e}")

# Fallback: bulk POST replaces the key.
url2 = f"https://api.netlify.com/api/v1/accounts/{acct}/env?site_id={site}"
payload = {"_json": [{"key": "AI_MODEL", "values": [{"value": NEW_MODEL, "context": "all"}]}]}
req = urllib.request.Request(
    url2,
    data=json.dumps(payload).encode(),
    headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
    method="POST",
)
try:
    r = urllib.request.urlopen(req, timeout=30)
    print(f"OK bulk POST {r.status}: AI_MODEL = {NEW_MODEL}")
except urllib.error.HTTPError as e:
    print(f"bulk HTTP {e.code}: {e.read()[:300]}")

# Verify
req = urllib.request.Request(
    f"https://api.netlify.com/api/v1/accounts/{acct}/env?site_id={site}",
    headers={"Authorization": f"Bearer {tok}"},
)
d = json.loads(urllib.request.urlopen(req, timeout=30).read())
for e in d:
    if e["key"] in ("AI_MODEL", "AI_BASE_URL"):
        print("  verify:", e["key"], "=", e["values"][0]["value"])