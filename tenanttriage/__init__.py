"""TenantTriage: local-first AI triage for rental inquiries.

Pipeline of three small agents, each with one job:
  1. Extractor agent  (extract.py)     -- facts, deterministically
  2. Screener agent   (rules.py)       -- landlord's criteria, deterministically
  3. Responder agent  (llm/templates)  -- phrasing only, guardrail-checked
"""
from __future__ import annotations

from .extract import extract
from .guardrails import validate_reply
from .llm import draft_with_model, ollama_available
from .rules import Criteria, evaluate
from .templates import template_reply
from .trace import Tracer


def triage(text: str, criteria: Criteria) -> dict:
    tracer = Tracer()
    with tracer.span("extractor-agent"):
        q = extract(text)
    with tracer.span("screener-agent"):
        v = evaluate(q, criteria)
    facts = {
        "name": q.name, "rent": criteria.rent, "status": v.status,
        "missing": v.missing, "pets_policy": criteria.pets_allowed,
        "move_in": q.move_in,
    }
    allowed_amounts = {criteria.rent}
    if q.monthly_income:
        allowed_amounts.add(q.monthly_income)
    source = "template"
    with tracer.span("responder-agent"):
        draft = None
        if ollama_available():
            draft = draft_with_model(facts)
        if draft:
            ok, problems = validate_reply(draft, allowed_amounts)
            if ok:
                source = "gemma-via-ollama"
            else:
                draft = None  # guardrail rejected it; fall through to template
        if not draft:
            draft = template_reply(q, criteria, v)
            ok, problems = validate_reply(draft, allowed_amounts)
            assert ok, f"built-in template failed its own guardrails: {problems}"
    return {
        "inquiry": q.__dict__, "verdict": v.__dict__,
        "reply_draft": draft, "reply_source": source,
        "trace": tracer.summary(),
        "disclaimer": (
            "Inquiry triage only, based on self-reported information. "
            "Not a credit, eviction, or background check, and not a rental decision."
        ),
    }
