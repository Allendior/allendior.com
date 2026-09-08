---
title: "Apex"
date: 2026-08-23
draft: false
tags: ["android", "python", "health", "local-first"]
description: "A private health-log bridge for meals and weigh-ins, designed around source-labelled records and deliberate sync instead of a cloud dashboard."
---

Apex is a personal health logging system for meals, weigh-ins, and training context. The public story is not the personal data—it is the engineering boundary: a dedicated Android app, a small Python relay, a local store, and explicit typed records rather than an all-access wellness platform.

The relay keeps meal and weigh-in entries separate from activity data, uses source labels, and is designed so a bad or unknown record type cannot quietly corrupt a different feed.

**Status:** Active personal tool
**Stack:** Android, Python, SQLite, Apple Shortcuts, private sync relay
