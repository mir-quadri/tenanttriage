"""Open-weight model layer: Gemma via Ollama, on the landlord's machine.

Design rules:
  - The model ONLY phrases a reply draft. Facts come from extraction/rules.
  - If Ollama is not running, callers fall back to built-in templates and
    the tool still works end to end. The model is an enhancement, never a
    single point of failure.
  - Model tag is a setting (OLLAMA_MODEL, default gemma3:4b) so the landlord
    can swap Gemma sizes or another open-weight model with no code change.
    Note: Gemma is an open-WEIGHT model under Google's Gemma terms; this
    project's MIT license covers this code only, not any model weights.
"""
from __future__ import annotations

import json
import os
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")


def ollama_available() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def draft_with_model(facts: dict, tone: str = "warm and professional") -> str | None:
    """Ask the local model to phrase a reply from verified facts only."""
    prompt = (
        "You draft short rental-inquiry replies for a landlord. Use ONLY the "
        "facts in this JSON. Never add prices, dates, or promises. Never say "
        "anyone is approved or denied. Ask for any missing items listed.\n"
        f"FACTS: {json.dumps(facts)}\nTone: {tone}. Reply in under 120 words."
    )
    body = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate", data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["response"].strip()
    except Exception:
        return None
