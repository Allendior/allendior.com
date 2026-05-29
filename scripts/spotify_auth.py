#!/usr/bin/env python3
"""
spotify_auth.py — One-time local script to obtain a Spotify refresh token.

Run this ONCE on your local machine, then save the printed refresh token
as the SPOTIFY_REFRESH_TOKEN secret in your GitHub repo settings.

Prerequisites
─────────────
1. In your Spotify Developer Dashboard (https://developer.spotify.com/dashboard):
   • Open your app → Edit Settings
   • Add  http://localhost:8888/callback  to Redirect URIs → Save

2. Set these env vars (or just paste your values below):
     export SPOTIFY_CLIENT_ID=<your client id>
     export SPOTIFY_CLIENT_SECRET=<your client secret>

Usage
─────
    python3 scripts/spotify_auth.py

The script will:
  1. Print an authorization URL — open it in your browser and log in
  2. Spotify redirects to localhost:8888/callback with a code
  3. The script exchanges the code for tokens and prints the refresh token
  4. Copy the refresh token and add it as SPOTIFY_REFRESH_TOKEN in:
     GitHub repo → Settings → Secrets and variables → Actions → New secret
"""

import base64
import http.server
import json
import os
import urllib.parse
import urllib.request
import webbrowser
from threading import Event

# ── Config ────────────────────────────────────────────────────────────────────

CLIENT_ID     = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()
REDIRECT_URI  = "http://localhost:8888/callback"
SCOPES        = "playlist-read-private playlist-read-collaborative"
PORT          = 8888

# ── Auth code capture ─────────────────────────────────────────────────────────

_auth_code: str | None = None
_done = Event()


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "error" in params:
            print(f"\n✗ Spotify returned an error: {params['error']}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Authorization failed. Check the terminal.</h2>")
            _done.set()
            return

        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"<h2>Authorization successful!</h2>"
                b"<p>You can close this tab and return to the terminal.</p>"
            )
            _done.set()
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h2>Unexpected callback. No code found.</h2>")

    def log_message(self, *_):
        pass  # silence request logging


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

    # Build the authorization URL
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
    print("  Spotify Authorization")
    print("─" * 60)
    print(f"\n  Make sure  {REDIRECT_URI}")
    print("  is listed as a Redirect URI in your Spotify app settings.\n")
    print("  Opening your browser to authorize…")
    print(f"\n  If the browser doesn't open, visit:\n  {auth_url}\n")
    print("─" * 60)

    webbrowser.open(auth_url)

    # Start local server and wait for callback
    server = http.server.HTTPServer(("localhost", PORT), _CallbackHandler)
    server.timeout = 120
    print(f"  Waiting for Spotify callback on port {PORT}…")

    while not _done.is_set():
        server.handle_request()

    server.server_close()

    if not _auth_code:
        print("✗ No authorization code received.")
        raise SystemExit(1)

    print("  Auth code received. Exchanging for tokens…\n")

    try:
        tokens = exchange_code(_auth_code)
    except Exception as exc:
        print(f"✗ Token exchange failed: {exc}")
        raise SystemExit(1)

    refresh_token = tokens.get("refresh_token", "")
    if not refresh_token:
        print("✗ No refresh_token in response:", tokens)
        raise SystemExit(1)

    print("─" * 60)
    print("  ✓ Success! Here is your refresh token:\n")
    print(f"  {refresh_token}\n")
    print("─" * 60)
    print("  Next steps:")
    print("  1. Copy the token above.")
    print("  2. Go to your GitHub repo → Settings → Secrets and variables")
    print("     → Actions → New repository secret")
    print("  3. Name: SPOTIFY_REFRESH_TOKEN")
    print("  4. Value: (paste the token)")
    print("  5. Push a commit or trigger a workflow run to test the sync.")
    print("─" * 60)


if __name__ == "__main__":
    main()
