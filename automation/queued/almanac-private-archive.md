---
title: "Almanac: A Private Archive Instead of a Photo Feed"
date: "__DATE__"
categories: ["Builds"]
tags: ["android", "privacy", "camerax", "local-first"]
description: "A local Android time capsule for one intentional portrait per day, built without feeds, analytics, or a cloud account."
draft: false
---

A long-term photo record can be valuable without becoming a performance.

**Almanac** is an Android project built around one simple practice: take one intentional portrait on a day when you want to remember it, then let the archive grow quietly over years.

There is no social layer, no streak counter, no reminder pressure, and no cloud account attached to the idea.

## The original photo is the record

The app keeps the image produced by the camera as the original. It does not crop, retouch, beautify, or run face analysis. A thumbnail may exist to make browsing usable, but the thumbnail is disposable; the original image is the archive.

That distinction is a design choice. I do not want an app that subtly changes the past while pretending to preserve it.

## Privacy is a technical property

The project stores its records in app-private device storage. It exports only when the person chooses a location through the Android system picker. Backups are disabled by default, and the app does not request network or location access.

Those are implementation details, but they are also the product promise. “Private” should be visible in the permissions, the storage model, and the way data leaves the device—not just in a landing-page sentence.

## Why build it

I am interested in software that helps a person remember their own life without turning that memory into a feed for someone else.

Almanac is a small experiment in that direction: a record, not a scorecard.
