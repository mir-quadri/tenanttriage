# Agent sessions — how TenantTriage was built

TenantTriage was designed and built with an AI agent as the build partner
(product-owner / designer / architect brief → working code), during the
Week 2 challenge window (Oct 12–18, 2026). This log is the honest record,
kept for the Best Use of Entire category and for any builder who forks this.

## Session 1 — Wed Oct 14, 2026 (design + v1 build)
- **Brief:** analyze the Hacktoberfest Week 2 reminder email, verify the
  challenge at the source (official DEV challenge page), and design ONE
  project for submission.
- **Verified facts that shaped the design:** theme is Side Hustle; deadline
  Oct 18, 11:59 PM PDT; 17 prize categories on the live page (the email
  said 16); writing quality is weighted most heavily; partner categories
  may only be claimed for technology genuinely used; project must be new
  and built inside the window; bonus points for a first user.
- **Decision:** landlord inquiry triage — because the builder is a real
  landlord with a live $800/mo vacancy and written screening criteria,
  giving the project a truthful first user, and because applicant PII makes
  the local/open-weight argument concrete rather than decorative.
- **Architecture rule set in this session:** the model never does
  arithmetic, dates, or decisions; deterministic extraction + criteria;
  guardrails validate every draft; templates keep the tool working with
  the model off; the landlord always sends.
- **Built:** package (`extract`, `rules`, `guardrails`, `llm`, `trace`,
  `templates`), zero-dependency web app + CLI, 4 fictional sample
  inquiries, `criteria.example.json`, `render.yaml`, MIT license.
- **What the agent got wrong, fixed in-session:** the credit-score regex
  only matched scores starting 6–8, so a stated 590 scored as "missing."
  A unit test caught it (590 → fair band); regex widened to 3–8xx and the
  full suite (10 tests) passes.
- **Verified end-to-end:** CLI on all samples; web app GET/POST smoke
  test; verdicts: complete inquiry → `ready_to_invite`; vague inquiry →
  `needs_info`; conflicting self-report → `landlord_review` with reasons.

## Session 2 — [date] (first-user run — fill in after Mir tests it)
- [ ] Ran TenantTriage on real (anonymized) inquiries for the Toledo unit
- [ ] What worked / what didn't:
- [ ] Would the first user pay? What did he ask for next?

## Session 3 — [date] (deploy + submission)
- [ ] Public GitHub repo created and pushed
- [ ] Render deploy live; URL added to README + DEV post
- [ ] DEV submission published before Oct 18, 11:59 PM PDT
