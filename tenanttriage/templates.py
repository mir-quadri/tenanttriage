"""Built-in reply templates: the always-works fallback, and the safety net
when a model draft fails guardrails. The landlord always edits and sends
the reply themselves -- TenantTriage never messages an applicant."""
from __future__ import annotations

from .extract import Inquiry
from .rules import Criteria, Verdict


def template_reply(q: Inquiry, c: Criteria, v: Verdict) -> str:
    name = (q.name or "there").split()[0]
    if v.status == "ready_to_invite":
        return (
            f"Hi {name}, thanks for your interest in the unit at ${c.rent:,}/month. "
            f"Based on what you shared, the next step is a formal application, which "
            f"includes credit and eviction-history verification. Would you like me to "
            f"send the application link and a few viewing times?"
        )
    if v.status == "landlord_review":
        return (
            f"Hi {name}, thanks for reaching out and for being upfront. I review every "
            f"inquiry against the same written criteria for the unit (${c.rent:,}/month). "
            f"I'm reviewing yours now and will get back to you shortly. If you'd like, "
            f"you can still submit a formal application so everything is on the record."
        )
    missing = ", ".join(v.missing) if v.missing else "a couple of details"
    return (
        f"Hi {name}, thanks for your interest in the unit at ${c.rent:,}/month. "
        f"So I can help properly, could you share: {missing}? "
        f"Every applicant is reviewed against the same criteria, and the formal "
        f"application includes credit and eviction-history verification."
    )
