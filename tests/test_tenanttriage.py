"""Run with: python3 -m unittest discover -s tests -v  (no pip installs)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tenanttriage import triage  # noqa: E402
from tenanttriage.extract import extract  # noqa: E402
from tenanttriage.guardrails import validate_reply  # noqa: E402
from tenanttriage.rules import Criteria, evaluate  # noqa: E402

C = Criteria(rent=800, income_multiple=3.0)


class TestExtract(unittest.TestCase):
    def test_income_and_name(self):
        q = extract("Hi, my name is Jordan Miller. I make $2,900 per month.")
        self.assertEqual(q.name, "Jordan Miller")
        self.assertEqual(q.monthly_income, 2900)

    def test_credit_score_bands(self):
        self.assertEqual(extract("my credit score is around 590").credit_described, "fair")
        self.assertEqual(extract("credit is 720").credit_described, "good")

    def test_eviction_stated_both_ways(self):
        self.assertFalse(extract("I have never been evicted").eviction_stated)
        self.assertTrue(extract("I was evicted once in 2023").eviction_stated)


class TestRules(unittest.TestCase):
    def test_ready(self):
        q = extract("I make $2,900 per month, good credit, never been evicted, move in November 1st")
        self.assertEqual(evaluate(q, C).status, "ready_to_invite")

    def test_missing_info(self):
        self.assertEqual(evaluate(extract("Is this available?"), C).status, "needs_info")

    def test_conflict_goes_to_human_not_auto_reject(self):
        q = extract("I earn $1,800 a month, credit score is around 590, I was evicted once")
        v = evaluate(q, C)
        self.assertEqual(v.status, "landlord_review")
        self.assertTrue(v.reasons)


class TestGuardrails(unittest.TestCase):
    def test_invented_amount_blocked(self):
        ok, problems = validate_reply("Rent is only $650, act fast!", {800})
        self.assertFalse(ok)
        self.assertTrue(any("invented amount" in p for p in problems))

    def test_decision_language_blocked(self):
        ok, _ = validate_reply("Good news, you are approved!", {800})
        self.assertFalse(ok)

    def test_clean_reply_passes(self):
        ok, _ = validate_reply("Thanks for asking about the $800 unit.", {800})
        self.assertTrue(ok)


class TestEndToEnd(unittest.TestCase):
    def test_triage_shape_and_disclaimer(self):
        r = triage("Hi, I'm Sam Lee, I make $3,000 per month, good credit, no evictions, move in November 1st", C)
        self.assertEqual(r["verdict"]["status"], "ready_to_invite")
        self.assertIn("Not a credit", r["disclaimer"])
        self.assertEqual(r["trace"]["marginal_cost_usd"], 0.0)
        self.assertTrue(r["reply_draft"])


if __name__ == "__main__":
    unittest.main()
