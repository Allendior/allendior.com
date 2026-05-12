# Errors

Command failures and integration errors.

---

## [ERR-20260511-001] hugo-build-missing

**Logged**: 2026-05-11T17:18:00-07:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Local Hugo build check failed because `hugo` is not installed on this Mac Mini.

### Error
`zsh:1: command not found: hugo`

### Context
- Command attempted: `hugo --minify`
- Repo: `~/allendior-site`
- Environment: local OpenClaw Mac Mini shell

### Suggested Fix
Install Hugo locally or rely on the GitHub Pages deploy pipeline for validation.

### Metadata
- Reproducible: yes
- Related Files: none
- Source: conversation

---
