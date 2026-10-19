# TenantTriage — Design Document
*Hacktoberfest Open-Source AI Challenge, Week 2: Side Hustle — product, design & architecture brief*
*Prepared Wed Oct 14, 2026 · Submission deadline: Sun Oct 18, 2026, 11:59 PM PDT (Mon Oct 19, 2:59 AM EDT)*

## 1. The challenge, verified at the source
- Theme: **Side Hustle** — build something with open-weight models or open-source AI that someone would actually pay for. Open-source AI must be what makes the project work.
- One overall winner ($250 + DEV++ + badge), 6 featured categories ($200 each), 11 partner categories ($100 each) — $2,550 across 18 winners. Valid submissions also get a completion badge.
- Judging: **writing quality is weighted most heavily**, then relevance to theme, creativity, technical execution, and (optional) use of partner technology.
- Rules that shape the design: brand-new project built inside Oct 12–18 window; public repo with an open-source license; one submission per challenge; teams up to 4; claim partner categories only for technology genuinely used.
- Email analysis note: the reminder email Mir received says 16 prize categories and mentions partner credits + DevRelay. The live challenge page says 17 categories (6 featured + 11 partner). **Trust the live page: 17.** The email also pitches DevRelay for saving agent sessions — optional, but judges like seeing the work.

## 2. Why this project (selection logic)
Scored against Mir's actual assets, not generic hackathon ideas:
- **A real, live user problem.** Mir owns a vacant 2-bed in Toledo at $800/mo and is placing a tenant *right now*, with hard criteria he set himself (good credit, no evictions). Every month vacant is $800 not collected. He is the first user — the challenge gives bonus points for landing one, and this one is truthful, not staged.
- **A named buyer.** Independent landlords (1–10 units) are too small for enterprise property platforms and too busy for inbox chaos. Inquiries arrive as messy listing-site messages; replies are slow, inconsistent, and — the quiet risk — occasionally worded in ways that create fair-housing exposure.
- **Open AI is load-bearing, not decorative.** Applicants share income, credit and eviction details. Sending that to a closed per-token API is a privacy and margin problem. A local open-weight model (Gemma via Ollama) keeps PII on the landlord's laptop and the marginal cost at $0 — which is exactly what makes a $15–19/mo price point viable (pricing is a hypothesis to test, §7).
- **White space in the field.** Reviewing live Week 2 submissions (Oct 14): invoice/receipt sorters, freelance tools, khata reminders, front desks for trades — no landlord inquiry-triage entry found. Commercial landlord AI exists (closed SaaS suites), which validates willingness to pay and gives the open/local angle a clear contrast.
- **Mir's signature.** A 3-agent pipeline mirrors his public brand — "I build agentic AI systems" — with the discipline from his payments career: the model never touches the decision.

## 3. Product definition
**TenantTriage is inquiry triage, deliberately NOT tenant screening.**
It does not run credit/eviction checks, produce a risk score, or approve/deny anyone. Those are regulated, consequential decisions. TenantTriage does the unglamorous hour before them:
1. Turns a messy inquiry into clean facts (name, stated income, stated credit, stated eviction history, occupants, pets, move-in date, questions asked).
2. Checks those self-reported facts against the landlord's *own written criteria* — the same criteria, applied the same way, to every inquiry.
3. Drafts the reply: invite to apply, ask for the missing pieces, or a neutral "under review" note — which the landlord reads, edits, and sends themselves.

Three verdicts only: `ready_to_invite` · `needs_info` · `landlord_review`. A conflict never auto-rejects; it routes to the human, with the reason stated in plain English.

**Primary user:** independent landlord with a live vacancy. **First user:** Mir, on his Toledo unit, using sample-anonymized inquiries for the public demo.

## 4. Design principles
1. **The model never does arithmetic, dates, or decisions.** Extraction and criteria are deterministic, tested code. The model only phrases.
2. **Every model output is checked before a human sees it.** Guardrails reject invented dollar amounts, decision language ("you are approved/denied"), and protected-class phrasing. Fail = safe built-in template.
3. **Works with the model off.** Ollama down? Templates carry the whole flow. The AI is an enhancement, never a single point of failure.
4. **Human sends, always.** TenantTriage drafts; it never messages an applicant. No auto-send exists in the codebase.
5. **Costs $0 to run.** Python standard library only. No pip installs, no API keys, no accounts. Clone → run.
6. **Honest by construction.** All output carries the disclaimer that it is based on self-reported information and is not a check or a decision.

## 5. Architecture
```
Inquiry text (paste / CLI / web form)
        │
 ┌──────▼───────┐   deterministic regex extraction, unit-tested
 │  EXTRACTOR   │   name · income · credit band · eviction stated ·
 │    AGENT     │   occupants · pets · move-in · questions
 └──────┬───────┘
 ┌──────▼───────┐   landlord's criteria.json, applied uniformly
 │  SCREENER    │   verdict + plain-English reasons + missing items
 │    AGENT     │
 └──────┬───────┘
 ┌──────▼───────┐   Gemma via Ollama if running, else templates
 │  RESPONDER   │──► GUARDRAILS: amounts whitelist · decision-language
 │    AGENT     │    block · protected-class block ──► fail = template
 └──────┬───────┘
   TRACER: one span per agent (ms, run id, $0 marginal cost) as JSON lines,
   forwarded to Sentry when SENTRY_DSN is set (Sentry Agent Tracing).
Output: facts + verdict + reasons + reply draft + trace + disclaimer
```
Stack: Python 3 stdlib (`http.server`) · Ollama + Gemma (open-weight, optional at runtime) · `render.yaml` for Render · MIT license (code only; model weights keep their own Gemma terms — stated plainly in README/LICENSE).

## 6. Partner-category strategy (genuine use only)
| Category | Prize | How it's genuinely used |
|---|---|---|
| Best Use of Gemma (featured) | $200 | Gemma via Ollama is the responder agent's model; tag is a setting, templates prove the contrast |
| Best Use of Render (featured) | $200 | `render.yaml` ships in-repo; live demo deploys there — *[deploy before publishing the post, then link it]* |
| Best Use of Sentry Agent Tracing | $100 | Every run emits per-agent spans; optional Sentry forwarding via `SENTRY_DSN` |
| Best Use of Entire | $100 | Build/agent sessions documented in `docs/agent-sessions.md` and linked in the post |
Not claimed: TabPFN, Tinker, Arduino, DigitalOcean, Backboard, ElevenLabs, GitHub Copilot, Mastra, MongoDB Atlas, SerpApi, Temporal, Tiger Data, .tech — not used, so not claimed. Claiming only what's real is both the rule and the brand.

## 7. Business model (hypothesis, labelled as such)
- Per-vacancy pricing fits how landlords think: **$19 per filled vacancy** or **$15/mo for active listers**. One day of vacancy on an $800/mo unit costs ~$27 — the tool pays for itself if it fills a unit one day faster.
- Costs: $0 inference (local model), $0 hosting at demo scale (Render free tier). That margin is only possible because the model is open-weight and local — the core of the "why open matters" story.
- No revenue is claimed anywhere. The post states the price as a hypothesis and reports the first-user test honestly.

## 8. Risks & mitigations
- **Fair-housing / legal:** no decisions, no scores, uniform written criteria, blocked-phrase guardrails, human sends, disclaimers everywhere. The post says explicitly this is not legal advice or a screening service.
- **Model hallucination:** model never supplies facts; guardrails whitelist dollar amounts against extracted facts.
- **Deadline (Oct 18, 11:59 PM PDT):** build is complete and tested Oct 14; Oct 15–17 are for GitHub push, Render deploy, first-user run, and the write-up (weighted most heavily — protect time for it).
- **No GitHub access from this workspace:** Mir creates/pushes the public repo (checklist provided); code is repo-ready as-is.

## 9. Roadmap (post-challenge, if it earns it)
Listing-site inbox import · criteria templates by state/locality with plain-English explanations · viewing-scheduler replies · Spanish reply drafts · a paid hosted tier for landlords who won't run Ollama (same open core, hosted Gemma).
