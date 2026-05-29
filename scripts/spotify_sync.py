#!/usr/bin/env python3
"""
spotify_sync.py — Sync a Spotify playlist to data/music.yaml

Environment variables required (set as GitHub Actions secrets):
  SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET
  SPOTIFY_PLAYLIST_ID   — bare ID only, e.g. 37i9dQZF1DXcBWIGoYBM5M
                          (the script strips URLs/URIs automatically)

Writes:
  data/music.yaml        — track list, overwritten on every successful sync

Never touches:
  data/music_moods.yaml  — your hand-maintained mood tags

On any failure the script exits 0 so the Hugo build continues
using whatever data/music.yaml already exists.
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR  = REPO_ROOT / "data"
OUT_FILE  = DATA_DIR / "music.yaml"


def _sanitize_playlist_id(raw: str) -> str:
    """
    Accept any of these formats and return the bare playlist ID:
      - 37i9dQZF1DXcBWIGoYBM5M                          (already bare)
      - https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
      - https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=xxx
      - spotify:playlist:37i9dQZF1DXcBWIGoYBM5M           (URI format)
    """
    raw = raw.strip()
    # URL format: extract the path segment after /playlist/
    m = re.search(r'/playlist/([A-Za-z0-9]+)', raw)
    if m:
        return m.group(1)
    # URI format: spotify:playlist:<id>
    m = re.search(r'spotify:playlist:([A-Za-z0-9]+)', raw)
    if m:
        return m.group(1)
    # Assume it's already a bare ID
    return raw


def _http(url: str, *, headers: dict = None, data: bytes = None) -> tuple[dict, int]:
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=20) as resp:
        status = resp.status
        body = json.loads(resp.read().decode())
    return body, status


def get_token(client_id: str, client_secret: str) -> str:
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp, status = _http(
        "https://accounts.spotify.com/api/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
    )
    print(f"  Token HTTP status: {status}")
    return resp["access_token"]


def fetch_tracks(playlist_id: str, token: str) -> list:
    """Fetch all tracks from a playlist, following pagination."""
    tracks = []
    # Don't use the fields filter — it can cause Spotify to return an
    # unexpected response structure. Fetch all fields and select locally.
    url = (
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        f"?limit=100"
    )
    auth = {"Authorization": f"Bearer {token}"}
    page_num = 0

    while url:
        page, status = _http(url, headers=auth)
        page_num += 1
        items = page.get("items", [])
        total = page.get("total", "?")
        print(f"  Page {page_num}: HTTP {status}, total={total}, items={len(items)}, "
              f"response keys={list(page.keys())}")

        for item in items:
            track = item.get("track")
            if not track or not track.get("id"):
                print(f"    Skipping null/local track (is_local={item.get('is_local')})")
                continue

            images = track.get("album", {}).get("images", [])
            # Prefer ~300 px; fall back to smallest available
            art_url = next(
                (img["url"] for img in images
                 if isinstance(img.get("width"), int) and img["width"] <= 300 and img.get("url")),
                images[-1]["url"] if images else "",
            )

            tracks.append({
                "track_id":      track["id"],
                "title":         track["name"],
                "artist":        ", ".join(a["name"] for a in track.get("artists", [])),
                "album":         track.get("album", {}).get("name", ""),
                "duration_ms":   track["duration_ms"],
                "spotify_url":   track.get("external_urls", {}).get("spotify", ""),
                "album_art_url": art_url,
            })
        url = page.get("next")

    return tracks


# ---------------------------------------------------------------------------
# YAML serialiser — no external dependencies needed
# ---------------------------------------------------------------------------

def _yaml_str(value: str) -> str:
    """Return a safely quoted YAML scalar for an arbitrary string."""
    if not value:
        return "''"
    must_quote = set(':#{}[],&*?|-<>=!%@\\')
    if any(c in must_quote for c in value) or value[0] in ('"', "'", ' ') or '\n' in value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def dump_music_yaml(synced_at: str, synced_display: str, tracks: list) -> str:
    lines = [
        f"synced_at: {_yaml_str(synced_at)}",
        f"synced_display: {_yaml_str(synced_display)}",
        "tracks:",
    ]
    for t in tracks:
        lines += [
            f"  - track_id:      {_yaml_str(t['track_id'])}",
            f"    title:         {_yaml_str(t['title'])}",
            f"    artist:        {_yaml_str(t['artist'])}",
            f"    album:         {_yaml_str(t['album'])}",
            f"    duration_ms:   {int(t['duration_ms'])}",
            f"    spotify_url:   {_yaml_str(t['spotify_url'])}",
            f"    album_art_url: {_yaml_str(t['album_art_url'])}",
        ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    client_id     = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()
    playlist_raw  = os.environ.get("SPOTIFY_PLAYLIST_ID", "").strip()

    # Debug: confirm each credential is present (never print values)
    print(f"  SPOTIFY_CLIENT_ID:     {'SET' if client_id     else 'MISSING'}")
    print(f"  SPOTIFY_CLIENT_SECRET: {'SET' if client_secret else 'MISSING'}")
    print(f"  SPOTIFY_PLAYLIST_ID:   {'SET' if playlist_raw  else 'MISSING'}")

    if not all([client_id, client_secret, playlist_raw]):
        print("⚠  Spotify credentials not set — skipping sync, keeping existing music.yaml")
        return

    playlist_id = _sanitize_playlist_id(playlist_raw)
    print(f"  Playlist ID (sanitized, last 4 chars): ...{playlist_id[-4:]}")

    try:
        print("→ Authenticating with Spotify …")
        token = get_token(client_id, client_secret)

        print(f"→ Fetching tracks from playlist …")
        tracks = fetch_tracks(playlist_id, token)
        print(f"  {len(tracks)} tracks fetched total")

        now = datetime.now(timezone.utc)
        synced_at      = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        synced_display = now.strftime("%d %b %Y, %H:%M UTC")

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        OUT_FILE.write_text(
            dump_music_yaml(synced_at, synced_display, tracks),
            encoding="utf-8",
        )
        print(f"✓ Wrote {OUT_FILE} ({len(tracks)} tracks, synced {synced_display})")

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        print(f"✗ Spotify HTTP {exc.code}: {body[:400]}")
        print("  Keeping existing data/music.yaml")

    except Exception as exc:
        print(f"✗ Spotify sync failed: {exc}")
        import traceback
        traceback.print_exc()
        print("  Keeping existing data/music.yaml")


if __name__ == "__main__":
    main()
