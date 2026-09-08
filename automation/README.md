# Allendior.com publication queue

This is a deliberately narrow automated publishing system.

- The scheduler may publish **only** the next item in `publication-queue.json` whose status is `queued`.
- Every queued Markdown file is fully written in advance and reviewed before it is added to the queue.
- The automation does not read personal logs, prompts, health data, notes, secrets, or arbitrary workspace files.
- Before a commit, it runs `hugo --minify`. A failed build must leave the queue untouched and must not push.
- It commits only the post and queue state, pushes to `main`, and GitHub Actions deploys Pages.
- If no queue item remains, it exits successfully without publishing and asks Allen to refill the reviewed queue.

The execution script is `scripts/publish_next.py`. The scheduled wrapper is installed under `~/.hermes/scripts/` because Hermes cron runs script paths from there.
