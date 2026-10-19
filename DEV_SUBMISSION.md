---
title: "TenantTriage: a local AI front desk for landlords who can't afford to miss an inquiry"
published: false
description: "I built a local-first, open-weight AI tool that triages rental inquiries against a landlord's own written criteria — because I am the landlord, the unit is vacant, and every day costs real money."
tags: devchallenge, hf26challenge, opensource, ai
# NOTE before publishing: the challenge submission template auto-adds the
# required tags (#devchallenge, #hf26challenge). Publish via the Week 2
# challenge page's "Side Hustle Submission Template" link so it counts.
# Fill every [BRACKET] first. Do not publish with brackets remaining.
---

*This is a submission for the Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle*

## What I Built

I own a two-bedroom rental unit in Toledo, Ohio. It rents for $800 a month, and right now it is vacant — which means every week I spend being slow, disorganized, or inconsistent with inquiries costs me real money. I am the user this tool was built for, and the vacancy is not a hypothetical.

The inquiries are the problem. They arrive as half-finished messages from listing sites: no income stated, a move-in date buried in a paragraph, three questions and none of them the one I need answered. Landlords with portfolios pay for platforms that handle this. Landlords with one or two units get an inbox — and improvise replies on a topic, housing, where improvised wording can create genuine legal risk.

**TenantTriage** is a local-first front desk for that inbox. Paste in a messy inquiry and it gives you back three things:

1. **The facts** — name, stated income, stated credit, stated eviction history, occupants, pets, move-in date, and the questions they asked. Extracted by deterministic, unit-tested code.
2. **A check against your own written criteria** — the same criteria, applied the same way, to every inquiry. It returns one of three verdicts: ready to invite to apply, needs more information (and lists exactly what's missing), or flagged for your personal review with the reason in plain English.
3. **A reply draft** — phrased by a local open-weight model (Gemma via Ollama) when one is running, or by built-in templates when it isn't. You read it, you edit it, you send it. The tool never messages an applicant.

What TenantTriage deliberately is **not**: a screening service. It runs no credit or eviction checks, produces no risk score, and never approves or denies anyone. It triages the hour *before* those steps, using only what the inquirer said about themselves, and every output carries that disclaimer.

## Demo

- **Live demo (Render):** [INSERT RENDER URL]
- Run it locally with zero installs: `python3 app.py` → http://localhost:8080

Real output, from the fictional sample inquiries in the repo (criteria: $800/mo rent, 3× income, good credit, no evictions, small dogs OK):

A complete inquiry comes back `ready_to_invite`, with a draft that moves the person to a formal application. A vague "is this available?" comes back `needs_info`, listing monthly income, eviction history, and credit as missing (its "asap" is extracted as a stated move-in intent, so move-in is not listed). An inquiry where the person honestly discloses $1,800/mo income and a past eviction comes back `landlord_review` — not rejected — with both reasons stated plainly, and a reply draft that thanks them for being upfront and keeps the door on the record. That last behavior is the product: consistency without automation making decisions it has no business making.

## Code

https://github.com/mir-quadri/tenanttriage — public, MIT licensed (repo created Oct 14, 2026; code upload pending as of Oct 15)

```
tenanttriage/
  extract.py     deterministic fact extraction (the model never does this)
  rules.py       the landlord's criteria, applied uniformly
  guardrails.py  every reply draft is validated before a human sees it
  llm.py         Gemma via Ollama — phrasing only, optional at runtime
  templates.py   built-in replies: the always-works fallback
  trace.py       one span per agent, per run (Sentry-forwardable)
app.py           zero-dependency web app + CLI (Python standard library)
tests/           10 tests, stdlib unittest, no pip installs
render.yaml      one-click Render deploy
```

## How I Built It

Three small agents, each with exactly one job — the same discipline I use in the agentic systems I build in my day work: **the model never does arithmetic, dates, or decisions.**

The extractor and the screener are plain Python with tests, because those are the parts a landlord might act on, and "the model said so" is not an acceptable source for a number. The responder is the only agent that touches the language model, and its output is treated as untrusted: guardrails reject any draft that invents a dollar amount (amounts are whitelisted against the extracted facts), uses approval/denial language, or contains protected-class phrasing. A rejected draft is replaced by a template, silently and safely.

Two build moments are worth sharing:

- A unit test caught my extractor scoring a stated credit score of 590 as "missing" — my regex only matched scores beginning with 6, 7, or 8. The fix was one character class. The lesson is the architecture: the bug was findable because extraction is code with tests, not a prompt I was vibes-checking.
- I started out wanting a "fit score." I deleted it. A single number that ranks people for housing, built by a hackathon project, is exactly the kind of thing that should not exist without serious rigor behind it. Three transparent verdicts with stated reasons are less flashy and more honest — and honesty is the feature landlords actually need when their criteria are questioned.

Every run emits an agent trace — a span per agent with timing and a marginal cost of $0.00, because local inference is free at the margin. Traces print as JSON locally and forward to Sentry when a DSN is configured.

## Why Open Innovation Matters Here

**Privacy is the product.** A rental inquiry is a named person telling you their income, their credit, and whether they've been evicted. Tools built on closed APIs ship that to someone else's server, per message, forever. TenantTriage runs Gemma on the landlord's own laptop through Ollama. The data never leaves the machine. That is not a philosophy preference; for this category of data, it is the difference between a tool a careful landlord can use and one they shouldn't.

**Zero marginal cost is the business model.** A side hustle for one-unit landlords only works at a one-unit price. My working hypothesis is $19 per filled vacancy, or $15/month while a unit is listed — one day of vacancy on my own unit costs about $27 in lost rent, so filling one day faster pays for the tool. That margin does not exist if every inquiry costs API tokens. It exists because the model is open-weight and local. (To be clear: this pricing is a hypothesis. I have taken no revenue for TenantTriage, and I won't claim otherwise.)

**No lock-in.** The model is one setting. A landlord can run a smaller Gemma on an old laptop or a bigger one on a desktop, or swap models entirely, without touching the pipeline — because extraction, criteria, and guardrails were never the model's job in the first place.

Where open fell short, honestly: a small local model is not a great writer of nuanced replies, which is precisely why its drafts are guardrail-checked, template-backed, and always human-sent. The system is designed to stay correct on the model's worst day.

## My First User

Me — which sounds like a dodge until you consider that I have a vacant unit, written criteria (good credit, no evictions — set before this project existed), and a manager I'm paying while it sits empty. TenantTriage was built against that real inbox problem, in that order.

[INSERT AFTER TESTING: 2–4 honest sentences — what you ran it on (anonymized real inquiries or samples), what it got right/wrong, whether you'd pay your own $19, and what you asked for next. Judges give bonus points for this section; do not invent it.]

What I asked for next, as the user: [e.g., viewing-time proposals in the reply draft / Spanish drafts / import from listing-site messages — pick what is true after your test.]

## Prize Categories

- **Best Use of Gemma** — Gemma, run locally via Ollama, is the responder agent's model; the model tag is a setting and the template fallback exists to prove the contrast.
- **Best Use of Render** — the live demo is deployed on Render from the `render.yaml` in the repo.
- **Best Use of Sentry Agent Tracing** — every triage run emits per-agent spans (extractor / screener / responder) with timing and cost; set `SENTRY_DSN` and they forward to Sentry's agent tracing.
- **Best Use of Entire** — the build's agent sessions are documented in `docs/agent-sessions.md` in the repo, including what the AI build partner got wrong.

## What's Next

If landlords besides me want it: listing-inbox import, viewing-scheduler replies, and a hosted tier running the same open core for landlords who won't run Ollama themselves. The repository stays MIT either way.
