---
title: "Why I’m Building Android Automation Around Signed Jobs"
date: 2026-09-07
categories: ["Builds"]
tags: ["android", "automation", "agents", "security"]
description: "Argo is my attempt to make Android automation explicit and bounded: signed, typed jobs instead of an agent with unlimited authority."
draft: false
---

The tempting version of an Android agent is simple: give it access to a phone, let a model inspect the screen, and ask it to do things.

The problem is that "do things" is not a permission boundary.

I’m building **Argo**, a control plane for Android actions, around a narrower idea: the phone should execute **signed, typed jobs**. A job says what is allowed to happen. The device verifies it and performs that bounded action. It does not need a language model living on the phone, deciding freely what should happen next.

## The design choice

A natural-language agent is useful for interpreting an intention. It is not, by itself, a good authorization system.

If an automation can read a screen, tap arbitrary coordinates, and keep improvising, then the line between a useful tool and an unsafe one gets blurry very fast. That may be acceptable for a disposable demo. It is not the standard I want for a device that contains real conversations, accounts, and payments.

So Argo separates the layers:

- a host can prepare a specific action request;
- the request has a typed shape rather than vague prose;
- the job is signed before it reaches the phone;
- the companion verifies it before executing;
- the result comes back as a structured record.

That is less magical. Good.

## Why typed jobs matter

A typed job forces the question that demo videos avoid: *what exactly is the agent allowed to do?*

Instead of granting a system a general power like “use this app,” a job can define a smaller operation and the fields it needs. That makes validation possible. It also makes failures easier to inspect: was the request malformed, did the device reject its signature, did the screen differ from what the operation expected, or did the action itself fail?

The constraint is the feature. It gives me somewhere concrete to put tests and safety checks.

## What is still unfinished

Argo is active development, not a finished product. The hard part is not making a phone tap a button. The hard part is deciding which actions should exist, how they are represented, how failures are reported, and when the system must hand control back to a human.

That is the work I’m interested in: not an agent that looks autonomous for thirty seconds, but a tool whose authority is understandable before it acts.

**Code:** [github.com/Allendior/private-agent](https://github.com/Allendior/private-agent)
