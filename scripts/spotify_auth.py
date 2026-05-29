#!/usr/bin/env python3
"""
spotify_auth.py — One-time local script to obtain a Spotify refresh token.

Run this ONCE on your local machine, then save the printed refresh token
as the SPOTIFY_REFRESH_TOKEN secret in your GitHub repo settings.

Prerequisites
─────────────
1. In your Spotify Developer Dashboard (https://developer.spotify.com/dashboard):
   • Open your app → Edit Settings
   • Add  https://allendior.com/callback  to Redirect URIs → Save

2. Set these env vars before running:
     export SPOTIFY_CLIENT_ID=<your client id>
     export SPOTIFY_CLIENT_SECRET=<your client secret>

Usage
─────
    python3 scripts/spotify_auth.py

The script will:
  1. Print an authorization URL — open it in your browser and log in
  2. Spotify redirects to https://allendior.com/callback?code=...
     (the page won't load, that's fine — copy the full URL from the address bar)
  3. Paste that URL here when prompted
  4. The script exchanges the code for tokens and prints the refresh token
  5. Add it as SPOTIFY_REFRESH_TOKEN in GitHub repo → Settings → Secrets
"""

import base64
import json
import os
import urllib.parse
import urllib.request

# ── Config ────────────────────────────────────────────────────────────────────

CLIENT_ID     = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()
REDIRECT_URI  = "https://allendior.com/callback"
SCOPES        = "user-read-private"

# ── Token exchange ────────────────────────────────────────────────────────────

def exchange_code(code: str) -> dict:
    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    body  = urllib.parse.urlencode({
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=body,
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("✗ SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set.")
        print("  export SPOTIFY_CLIENT_ID=<id>")
        print("  export SPOTIFY_CLIENT_SECRET=<secret>")
        raise SystemExit(1)

    auth_url = (
        "https://accounts.spotify.com/authorize?"
        + urllib.parse.urlencode({
            "client_id":     CLIENT_ID,
            "response_type": "code",
            "redirect_uri":  REDIRECT_URI,
            "scope":         SCOPES,
        })
    )

    print("─" * 60)
    print("  Step 1 — Open this URL in your browser:")
    print()
    print(f"  {auth_url}")
    print()
    print("  Step 2 — Log in to Spotify and approve access.")
    print()
    print("  Step 3 — You'll be redirected to a URL starting with:")
    print(f"  {REDIRECT_URI}?code=...")
    print("  The page won't load — that's expected.")
    print("  Copy the FULL URL from your browser's address bar.")
    print("─" * 60)

    pasted = input("\n  Paste the full redirect URL here and press Enter:\n  ").strip()

    if not pasted:
        print("✗ Nothing pasted.")
        raise SystemExit(1)

    parsed = urllib.parse.urlparse(pasted)
    params = urllib.parse.parse_qs(parsed.query)

    if "error" in params:
        print(f"✗ Spotify returned an error: {params['error']}")
        raise SystemExit(1)

    if "code" not in params:
        print("✗ No 'code' parameter found in the URL.")
        print(f"  Got: {pasted}")
        raise SystemExit(1)

    code = params["code"][0]
    print("\n  Exchanging code for tokens…")

    try:
        tokens = exchange_code(code)
    except Exception as exc:
        print(f"✗ Token exchange failed: {exc}")
        raise SystemExit(1)

    refresh_token = tokens.get("refresh_token", "")
    if not refresh_token:
        print("✗ No refresh_token in response:", tokens)
        raise SystemExit(1)

    print()
    print("─" * 60)
    print("  ✓ Success! Your refresh token:\n")
    print(f"  {refresh_token}")
    print()
    print("─" * 60)
    print("  Next steps:")
    print("  1. Copy the token above.")
    print("  2. GitHub repo → Settings → Secrets and variables")
    print("     → Actions → New repository secret")
    print("  3. Name:  SPOTIFY_REFRESH_TOKEN")
    print("  4. Value: (paste the token)")
    print("  5. Run:   gh workflow run deploy.yml --repo Allendior/allendior.com")
    print("─" * 60)


if __name__ == "__main__":
    main()
