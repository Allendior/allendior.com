---
title: "Weekly Grocery Automation"
date: 2026-06-01
draft: false
tags: ["python", "playwright", "automation", "ai agents", "telegram"]
description: "An AI agent that automatically builds my Instacart cart every week, logs prices, and notifies me on Telegram — so I never run out of food."
---

## The Problem

I kept forgetting to buy groceries. Not occasionally — consistently. I'd run out of food, tell myself I'd order later, and later never came. It was affecting my health and energy levels, so I decided to automate the entire thing.

## What I Built

A fully automated grocery pipeline that runs every Sunday at 9am:

1. Reads a JSON grocery list I maintain by texting my AI agent ("add chicken thighs", "milk is empty")
2. Launches a headless Playwright browser with a persisted Instacart session
3. Searches each item on Instacart, picks the best match, and adds it to cart
4. Logs each item's name, price, and quantity to a local CSV for spend tracking
5. Sends a Telegram summary to my group chat with a direct checkout link

I review the cart, tap checkout, and the groceries arrive. That's my only job.

## Tech Stack

- **Python** — core automation script
- **Playwright** — headless browser automation with cookie-based session persistence
- **Hermes** — local AI agent runtime handling cron scheduling and Telegram delivery
- **JSON / CSV** — grocery list storage and price logging
- **Instacart** — delivery platform (Kelowna, BC)
- **Telegram** — notification and list management interface

## How the List Works

I text my agent natural language and it updates the grocery list in real time:
"add Greek yogurt"       → appended to grocery-list.json
"milk is empty"          → appended to grocery-list.json
"show grocery list"      → returns current list on Telegram
"clear grocery list"     → resets after order is placed
"how much did I spend"   → summarizes grocery-price-log.csv

## Price Tracking

Every weekly run appends a structured row to a local CSV:

| logged_at | item_name | quantity | price_text | store | status |
|---|---|---|---|---|---|
| 2026-06-01 | 3% fat milk | 1 | $6.49 | Instacart | added |

Over time this builds a clear picture of what things cost week to week — useful for spotting price spikes or finding cheaper alternatives.

## Key Challenge

Instacart blocks headless browsers at the network level (403 Forbidden). The fix was to authenticate once using a visible Playwright window (`headless=False`), save the session cookies to disk, and inject them into every subsequent headless run. The session persists indefinitely as long as it stays active.

## Result

Groceries arrive every week without me thinking about it. The whole checkout interaction takes under 30 seconds — just a Telegram tap.
