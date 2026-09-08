#!/usr/bin/env python3
"""Publish exactly one reviewed Allendior.com build note.

This script intentionally has no content-generation step. It only moves the next
pre-written entry from automation/publication-queue.json into Hugo content, builds
the site, commits the precise files, and pushes main.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "automation" / "publication-queue.json"
CONTENT_DIR = ROOT / "content" / "writing"
TZ = ZoneInfo("America/Vancouver")


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def load_queue() -> dict:
    with QUEUE_PATH.open() as fh:
        return json.load(fh)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    queue = load_queue()
    item = next((x for x in queue["items"] if x["status"] == "queued"), None)
    if item is None:
        print("No reviewed website post is queued; nothing published.")
        return 0

    source = ROOT / item["path"]
    if not source.is_file():
        raise SystemExit(f"Queue source is missing: {source}")
    destination = CONTENT_DIR / f"{item['id']}.md"
    if destination.exists():
        raise SystemExit(f"Refusing to overwrite existing post: {destination}")

    date = dt.datetime.now(TZ).date().isoformat()
    text = source.read_text(encoding="utf-8")
    if "__DATE__" not in text:
        raise SystemExit("Queued post must contain the __DATE__ placeholder.")
    rendered = text.replace("__DATE__", date)

    if args.dry_run:
        print(f"Would publish {item['id']} as {destination.relative_to(ROOT)} dated {date}.")
        return 0

    destination.write_text(rendered, encoding="utf-8")
    item["status"] = "published"
    item["published_at"] = dt.datetime.now(TZ).isoformat(timespec="seconds")
    item["published_path"] = str(destination.relative_to(ROOT))
    QUEUE_PATH.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")

    committed = False
    try:
        run("hugo", "--minify")
        run("git", "add", str(destination.relative_to(ROOT)), str(QUEUE_PATH.relative_to(ROOT)))
        run("git", "commit", "-m", f"content: publish {item['project']} build note")
        committed = True
        run("git", "push", "origin", "main")
    except Exception:
        # Before a commit, restore the queue so a corrected build can retry cleanly.
        # After a commit, retain the exact committed state: a later retry can push it
        # safely, and we never pretend an already committed publication disappeared.
        if not committed:
            if destination.exists():
                destination.unlink()
            queue = load_queue()
            for candidate in queue["items"]:
                if candidate["id"] == item["id"]:
                    candidate["status"] = "queued"
                    candidate.pop("published_at", None)
                    candidate.pop("published_path", None)
            QUEUE_PATH.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
        raise

    print(f"Published {item['id']} and pushed main.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
