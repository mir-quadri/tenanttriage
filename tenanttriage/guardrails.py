"""Guardrails on anything the model (or a template) says to an applicant.

A reply draft is only shown to the landlord if it passes every check:
  1. No protected-class or discriminatory language (fair-housing risk).
  2. No invented money: every $ amount in the draft must come from the inquiry
     or the criteria.
  3. No decision language: the tool drafts replies, it never approves,
     denies, or promises a unit to anyone.
If a draft fails, the landlord gets a safe built-in template instead.
"""
from __future__ import annotations

import re

BLOCKED_PHRASES = [
    "no kids", "no children", "adults only", "perfect for singles",
    "young professionals only", "no foreigners", "christians only",
    "you are approved", "you're approved", "you are denied", "you're denied",
    "guaranteed approval", "we will rent to you",
]
DECISION_WORDS = ["approved", "denied", "rejected"]


def validate_reply(text: str, allowed_amounts: set[int]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    low = text.lower()
    for phrase in BLOCKED_PHRASES:
        if phrase in low:
            problems.append(f"blocked phrase: '{phrase}'")
    for amt in re.findall(r"\$\s?([\d,]+)", text):
        try:
            if int(amt.replace(",", "")) not in allowed_amounts:
                problems.append(f"invented amount: ${amt}")
        except ValueError:
            problems.append(f"unparseable amount: ${amt}")
    return (not problems), problems
