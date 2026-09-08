---
title: "Building a Private Map of the Places That Matter"
date: "__DATE__"
categories: ["Builds"]
tags: ["android", "privacy", "offline-first", "kotlin"]
description: "A local-first Android app for place memories, designed around portable data rather than a social map feed."
draft: false
---

Most map products want to become a feed: places to rate, photos to share, people to follow, recommendations to react to.

I wanted something quieter: a private record of the places that actually matter to me.

**Map of Exploration** is an offline Android project for saving a place memory—a title, category, optional note, and optional coordinates—without creating another account, social graph, or tracking surface.

## The data should outlive the app

The core requirement is portability. A place record is a validated UUID, timestamp, and small set of fields that can be exported as a schema-versioned JSON archive.

That means the app is not the only place the memories exist. Import is validated before anything changes, exports are explicit, and merging uses the record UUID so an archive can be moved without multiplying entries.

This is less flashy than an infinite map or recommendation engine. It is also easier to trust.

## Local by default

The MVP stores memories with Room on the device. It has no network client, no credentials, and no Android permissions beyond what the narrow feature set needs. A memory stays local unless I deliberately export it.

There is a useful design constraint in that: I cannot pretend the difficult parts are someone else’s infrastructure problem. If an import is malformed, it has to be rejected cleanly. If the archive changes, its version needs to be visible. If I want syncing later, that is a separate design decision instead of an accidental side effect.

## What I’m learning

The project is not about building a better Google Maps clone. It is practice in a product question I care about: how do you make personal software feel durable without turning it into a cloud service that owns the person’s life?

The first answer is modest. Keep the data format understandable. Keep the boundaries narrow. Make export real.
