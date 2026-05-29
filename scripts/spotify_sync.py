#!/usr/bin/env python3
"""
spotify_sync.py — Sync a Spotify playlist to data/music.yaml

Environment variables required (set as GitHub Actions secrets):
  SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET
  SPOTIFY_PLAYLIST_ID

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


def _http(url: str, *, headers: dict = None, data: bytes = None) -> dict:
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def get_token(client_id: str, client_secret: str) -> str:
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = _http(
        "https://accounts.spotify.com/api/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
    )
    return resp["access_token"]


def fetch_tracks(playlist_id: str, token: str) -> list:
    """Fetch all tracks from a playlist, following pagination."""
    tracks = []
    fields = "next,items(track(id,name,duration_ms,external_urls,album(name,images),artists))"
    url = (
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        f"?limit=100&fields={urllib.parse.quote(fields)}"
    )
    auth = {"Authorization": f"Bearer {token}"}

    while url:
        page = _http(url, headers=auth)
        for item in page.get("items", []):
            track = item.get("track")
            if not track or not track.get("id"):
                continue  # skip null / local tracks

            # Prefer a ~300 px image; fall back to the last (smallest) one
            images = track.get("album", {}).get("images", [])
            art_url = next(
                (img["url"] for img in images if img.get("width", 0) <= 300 and img.get("url")),
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
    # Characters that force quoting
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
    playlist_id   = os.environ.get("SPOTIFY_PLAYLIST_ID", "").strip()

    if not all([client_id, client_secret, playlist_id]):
        print("⚠  Spotify credentials not set — skipping sync, keeping existing music.yaml")
        return

    try:
        print("→ Authenticating with Spotify …")
        token = get_token(client_id, client_secret)

        print(f"→ Fetching tracks from playlist {playlist_id} …")
        tracks = fetch_tracks(playlist_id, token)
        print(f"  {len(tracks)} tracks fetched")

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
        print(f"✗ Spotify HTTP {exc.code}: {body[:200]}")
        print("  Keeping existing data/music.yaml")

    except Exception as exc:
        print(f"✗ Spotify sync failed: {exc}")
        print("  Keeping existing data/music.yaml")


if __name__ == "__main__":
    main()
