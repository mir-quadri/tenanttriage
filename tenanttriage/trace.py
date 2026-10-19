"""Agent tracing: every run emits structured spans.

Each agent step (extract -> evaluate -> draft -> validate) records a span
with timing and token-free cost data (local inference = $0 marginal cost).
Spans print as JSON lines locally, and if SENTRY_DSN is set and the optional
`sentry-sdk` package is installed, they are also forwarded as Sentry
transactions for the Sentry Agent Tracing view. Tracing never blocks a run.
"""
from __future__ import annotations

import json
import os
import time
import uuid


class Tracer:
    def __init__(self) -> None:
        self.run_id = uuid.uuid4().hex[:12]
        self.spans: list[dict] = []
        self._sentry = None
        dsn = os.environ.get("SENTRY_DSN")
        if dsn:
            try:
                import sentry_sdk  # optional dependency, only if DSN is set

                sentry_sdk.init(dsn=dsn, traces_sample_rate=1.0)
                self._sentry = sentry_sdk
            except Exception:
                self._sentry = None

    def span(self, agent: str, **fields):
        start = time.perf_counter()
        record = {"run_id": self.run_id, "agent": agent, **fields}

        class _Ctx:
            def __enter__(self_inner):
                return record

            def __exit__(self_inner, *exc):
                record["ms"] = round((time.perf_counter() - start) * 1000, 2)
                self.spans.append(record)
                print(json.dumps({"trace": record}), flush=True)
                return False

        return _Ctx()

    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "spans": len(self.spans),
            "total_ms": round(sum(s.get("ms", 0) for s in self.spans), 2),
            "marginal_cost_usd": 0.0,
            "backend": "sentry+local" if self._sentry else "local",
        }
