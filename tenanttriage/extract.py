"""Deterministic extraction from a raw rental inquiry.

The model never does this job alone. Everything a landlord might act on
(dates, money, counts) is pulled out by plain, tested code first, so the
language model can only phrase things -- it cannot invent the facts.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Inquiry:
    raw: str
    name: str | None = None
    occupants: int | None = None
    monthly_income: int | None = None
    credit_described: str | None = None  # "good" | "fair" | "poor" | None
    eviction_stated: bool | None = None  # True = applicant states an eviction
    pets: str | None = None
    move_in: str | None = None
    questions: list[str] = field(default_factory=list)


_NAME = re.compile(r"(?:my name is|i am|i'm|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", re.I)
_INCOME = re.compile(r"\$\s?([\d,]{3,})\s*(?:/|per\s+)?(?:a\s+)?month|(?:make|earn|income(?:\s+is)?)\s+\$?\s?([\d,]{3,})", re.I)
_OCCUPANTS = re.compile(r"(\d+)\s*(?:people|persons|adults|occupants|of us)", re.I)
_MOVEIN = re.compile(r"(?:move(?:\s+in)?|start|available|need(?:\s+it)?(?:\s+by)?)\s+(?:on\s+|by\s+)?((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?|next month|asap|immediately)", re.I)


def extract(text: str) -> Inquiry:
    q = Inquiry(raw=text)
    m = _NAME.search(text)
    if m:
        q.name = m.group(1).strip()
    m = _INCOME.search(text)
    if m:
        raw_amt = (m.group(1) or m.group(2) or "").replace(",", "")
        if raw_amt.isdigit():
            q.monthly_income = int(raw_amt)
    m = _OCCUPANTS.search(text)
    if m:
        q.occupants = int(m.group(1))
    low = text.lower()
    if "no eviction" in low or "never been evicted" in low or "no evictions" in low:
        q.eviction_stated = False
    elif "eviction" in low or "was evicted" in low:
        q.eviction_stated = True
    if re.search(r"credit(?:\s+score)?\s*(?:is\s*)?(?:around\s*)?([3-8]\d\d)", low):
        score = int(re.search(r"credit(?:\s+score)?\s*(?:is\s*)?(?:around\s*)?([3-8]\d\d)", low).group(1))
        q.credit_described = "good" if score >= 650 else "fair" if score >= 580 else "poor"
    elif "good credit" in low or "excellent credit" in low or "great credit" in low:
        q.credit_described = "good"
    elif "fair credit" in low:
        q.credit_described = "fair"
    elif "bad credit" in low or "poor credit" in low:
        q.credit_described = "poor"
    pet = re.search(r"(small dog|dog|cat|no pets|pet)", low)
    if pet:
        q.pets = "none stated as pets" if "no pets" in low else pet.group(1)
    m = _MOVEIN.search(text)
    if m:
        q.move_in = m.group(1).strip()
    q.questions = [s.strip() for s in re.split(r"(?<=[?])\s+", text) if "?" in s]
    return q
