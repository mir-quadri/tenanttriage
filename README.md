# TenantTriage

**A local-first AI front desk for independent landlords.**
Paste a messy rental inquiry → get the clean facts, a check against *your own written criteria*, and a reply draft you review and send yourself. Applicant details never leave your machine.

Built for the **Hacktoberfest Open-Source AI Challenge: Week 2 — Side Hustle**.

## The problem

A vacant unit earns $0 while inquiries pile up as half-finished listing-site messages: no income stated, move-in date buried in a paragraph, the one question that matters unanswered. Independent landlords (1–10 units) reply late, reply inconsistently, and improvise wording on a topic — housing — where improvised wording can create real legal exposure. Enterprise platforms solve this for portfolios, at portfolio prices.

## What it does

Three small agents, each with one job:

1. **Extractor agent** (deterministic, tested) — pulls out name, stated income, stated credit, stated eviction history, occupants, pets, move-in date, and the applicant's questions.
2. **Screener agent** (deterministic, tested) — applies *your* criteria file, the same way, to every inquiry. Three outcomes: `ready_to_invite`, `needs_info`, or `landlord_review` (a human decides — the tool never does).
3. **Responder agent** — phrases the reply. With a local open-weight model (Gemma via Ollama) it drafts in your tone; every draft passes guardrails (no invented dollar amounts, no "approved/denied" language, no protected-class phrasing) or a safe built-in template replaces it. With no model running, templates carry the whole flow.

Every run emits a per-agent trace (timing, run id, $0 marginal cost), forwarded to Sentry if you set `SENTRY_DSN`.

> **What this is not:** not a credit, eviction, or background check, not a risk score, and not a rental decision. It triages *inquiries* using *self-reported* information, and says so on every output.

## Run it (zero installs)

```bash
git clone <this-repo> && cd tenanttriage
python3 app.py                      # web app on http://localhost:8080
python3 app.py --cli samples/inquiry-1.txt   # or triage from the CLI
python3 -m unittest discover -s tests -v     # 10 tests, stdlib only
```

Optional — model-drafted replies (everything else works without it):

```bash
ollama pull gemma3:4b && ollama serve
```

Your criteria: copy `criteria.example.json` to `criteria.json`, edit (rent, income multiple, eviction/credit criteria, pet policy), then run with `CRITERIA=criteria.json python3 app.py`.

Deploy: `render.yaml` is included for a one-click Render web service. A hosted deploy runs on templates unless you point `OLLAMA_URL` at a model host — no functionality is mocked.

## Why open-source AI is the business model

- **Privacy is the product.** Inquiries contain income, credit, and eviction details about named people. With a local open-weight model, that data never leaves the landlord's laptop — a claim no closed-API tool can make.
- **$0 marginal cost is the margin.** A closed API charges per message forever. Local inference costs nothing per inquiry, which is what makes a $15–19 price point for a one-unit landlord viable at all. (Pricing is a hypothesis being tested with the first user — no revenue is claimed.)
- **No lock-in.** The model tag is one setting. Swap Gemma sizes, or another open-weight model, without touching the pipeline — extraction, criteria, and guardrails are model-independent.

## First user

The builder is an independent landlord with a live vacancy (2-bed, $800/mo, Toledo OH; written criteria: good credit, no evictions, small dogs OK — that's `criteria.example.json`). TenantTriage was built for that inbox first. Demo inquiries in `samples/` are fictional.

## Prize categories entered

- **Best Use of Gemma** — Gemma via Ollama is the responder agent's model.
- **Best Use of Sentry Agent Tracing** — per-agent spans on every run, Sentry forwarding via `SENTRY_DSN`.
- **Best Use of Entire** — build/agent sessions in `docs/agent-sessions.md`.

## License

MIT for this code (see `LICENSE`). Connected models keep their own terms — Gemma is an open-weight model under Google's Gemma terms; this project's license does not cover model weights.
