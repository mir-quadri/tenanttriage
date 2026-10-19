"""The landlord's own written criteria, applied the same way every time.

TenantTriage is an INQUIRY triage tool, not a screening decision service.
It never approves or rejects anyone. It sorts an inquiry into:
  - ready_to_invite   : self-reported info matches the stated criteria
  - needs_info        : something the criteria need is missing / unclear
  - landlord_review   : self-reported info conflicts with a stated criterion;
                        a human landlord decides what happens next
All inputs are SELF-REPORTED by the inquirer. Nothing here is a credit,
eviction, or background check, and the output says so.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from .extract import Inquiry


@dataclass
class Criteria:
    rent: int = 800
    income_multiple: float = 3.0
    require_no_evictions: bool = True
    require_good_credit: bool = True
    pets_allowed: str = "small dogs OK"
    max_occupants: int | None = None

    @staticmethod
    def load(path: str) -> "Criteria":
        with open(path, encoding="utf-8") as f:
            return Criteria(**json.load(f))


@dataclass
class Verdict:
    status: str
    reasons: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


def evaluate(q: Inquiry, c: Criteria) -> Verdict:
    v = Verdict(status="needs_info")
    if q.monthly_income is None:
        v.missing.append("monthly income")
    elif q.monthly_income < c.rent * c.income_multiple:
        v.reasons.append(
            f"Stated income ${q.monthly_income:,}/mo is below the stated "
            f"{c.income_multiple:g}x-of-rent criterion (${int(c.rent * c.income_multiple):,}/mo for ${c.rent:,}/mo rent)."
        )
    if c.require_no_evictions:
        if q.eviction_stated is None:
            v.missing.append("eviction history")
        elif q.eviction_stated:
            v.reasons.append("Inquirer states a prior eviction; the listing criterion is no evictions.")
    if c.require_good_credit:
        if q.credit_described is None:
            v.missing.append("credit description")
        elif q.credit_described == "poor":
            v.reasons.append("Inquirer describes their credit as poor; the listing criterion is good credit.")
    if q.move_in is None:
        v.missing.append("desired move-in date")
    if v.reasons:
        v.status = "landlord_review"
    elif v.missing:
        v.status = "needs_info"
    else:
        v.status = "ready_to_invite"
    return v
