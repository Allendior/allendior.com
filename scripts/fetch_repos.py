#!/usr/bin/env python3
"""
fetch_repos.py — Fetch public GitHub repos and write data/github_repos.json

Fetches the 20 most-recently-pushed non-fork repos for a GitHub user
and writes a filtered JSON array to data/github_repos.json.

Falls back to an empty array and exits 0 on any network error so the
Hugo build continues with whatever data file already exists.
"""

import json
import urllib.error
import urllib.request
from pathlib import Path

GITHUB_USER = "Allendior"
API_URL = (
    f"https://api.github.com/users/{GITHUB_USER}/repos"
    "?sort=updated&per_page=20&type=owner"
)
OUT_FILE = Path(__file__).resolve().parent.parent / "data" / "github_repos.json"

KEEP_FIELDS = ("name", "description", "language", "stargazers_count", "pushed_at", "html_url")


def fetch() -> list:
    req = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        repos = json.loads(resp.read().decode())

    return [
        {k: (r.get(k) or "") if k in ("description", "language") else r[k] for k in KEEP_FIELDS}
        for r in repos
        if not r["fork"] and r["name"].lower() != GITHUB_USER.lower()
    ]


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        repos = fetch()
        OUT_FILE.write_text(json.dumps(repos, indent=2), encoding="utf-8")
        print(f"✓ Wrote {len(repos)} repos to {OUT_FILE.name}")
    except Exception as exc:
        print(f"✗ GitHub fetch failed: {exc}")
        print("  Keeping existing data/github_repos.json (or writing empty fallback)")
        if not OUT_FILE.exists():
            OUT_FILE.write_text("[]", encoding="utf-8")


if __name__ == "__main__":
    main()
