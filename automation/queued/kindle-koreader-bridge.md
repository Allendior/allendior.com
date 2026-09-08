---
title: "A Small Kindle Library Bridge, Built Around Ownership"
date: "__DATE__"
categories: ["Builds"]
tags: ["python", "self-hosting", "ebooks", "local-first"]
description: "A private, local pipeline for taking owned ebooks from a Mac into KOReader without treating a library as a platform subscription."
draft: false
---

Reading on an e-ink device should not require giving up control of a personal library.

I built a small bridge for my own owned ebooks: a file enters through a narrow intake script, gets organized in Calibre, and becomes available to KOReader through a private OPDS catalog.

The point is not to build a replacement bookstore. It is to make the books I already own easy to use on the device I actually read from.

## The unglamorous parts are the product

The intake script accepts a limited set of ebook formats and rejects missing files and symlinks. It also uses a SHA-256 digest to detect duplicates, so rerunning the same book does not create a second copy in the catalog.

Those choices are not exciting, but they are the difference between a one-off script and a tool I can use without wondering what it did last time.

## A private delivery path

Calibre provides the library and OPDS catalog. KOReader can browse it from the device over a private network. Authentication exists, but it is not a public service and it is not exposed to the open internet.

That boundary matters. A library is personal infrastructure. It should work without an account system, recommendations, ads, or a company deciding which reading device gets to participate.

## What this project taught me

I keep coming back to the same question: can small software respect a person’s ownership without becoming fragile?

The answer is usually not a huge platform. It is a clear pipeline, a tight set of supported inputs, a reversible setup, and tests for the failure modes people hit in ordinary use.
