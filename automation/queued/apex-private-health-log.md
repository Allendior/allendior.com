---
title: "Apex: Building a Health Log Without Turning My Body Into a Cloud Product"
date: "__DATE__"
categories: ["Builds"]
tags: ["android", "python", "privacy", "personal-software"]
description: "Apex is a private health-log bridge for meals and weigh-ins, built around narrow data types and explicit sync."
draft: false
---

Health tracking apps usually ask for everything: an account, a permanent cloud record, device permissions, and a feed of scores that starts to feel like another place to fail.

I wanted a narrower tool.

**Apex** is a personal logging system for meals, weigh-ins, and training context. It is not a diagnosis engine, a social challenge, or a wellness brand. It is an attempt to make the data I choose to track easier to capture and easier to own.

## Keep the records typed

One reliability decision mattered more than any dashboard: a meal is not a step count, and a weigh-in is not a workout.

The relay uses distinct record types and source labels. Activity data has a separate route from meals and weigh-ins. That is intentionally boring, but it prevents a future shortcut or device integration from silently pushing an unknown record into the wrong feed.

A useful personal system should be able to say: *I do not know what this is, so I will not store it as something else.*

## A small bridge, not an extraction pipeline

The current setup uses an Android app alongside a small Python relay and a local store. Sync is deliberate. The point is not to collect every signal from my body; it is to make a few chosen inputs—like food and bodyweight—available where I can use them.

That boundary keeps the project honest. I can improve a logging workflow without pretending an app knows my health better than I do.

## What remains hard

The difficult work is not calculating calories or drawing a graph. It is keeping sources clear, preventing duplicates, handling offline or stale data, and making sure a sync failure is visible rather than silently invented away.

That is the kind of personal software I want to build: private enough to be mine, simple enough to audit, and clear enough to distrust when it should be distrusted.
