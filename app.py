#!/usr/bin/env python3
"""TenantTriage -- zero-dependency web app + CLI (Python standard library only).

Run the web app:   python3 app.py            -> http://localhost:8080
Run the CLI:       python3 app.py --cli samples/inquiry-1.txt
Use your criteria: CRITERIA=criteria.json python3 app.py
With a local model: ollama pull gemma3:4b && ollama serve  (optional)
"""
from __future__ import annotations

import html
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tenanttriage import Criteria, triage  # noqa: E402

CRITERIA_PATH = os.environ.get("CRITERIA", os.path.join(os.path.dirname(__file__), "criteria.example.json"))
CRITERIA = Criteria.load(CRITERIA_PATH) if os.path.exists(CRITERIA_PATH) else Criteria()

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TenantTriage -- local AI front desk for independent landlords</title>
<style>body{{font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem}}
textarea{{width:100%}}pre{{background:#f4f4f4;padding:1rem;white-space:pre-wrap}}
.note{{color:#555;font-size:.9rem}}</style></head><body>
<h1>TenantTriage</h1>
<p>Paste a rental inquiry. Get the facts, a check against <em>your</em> written
criteria, and a reply draft you review and send yourself. Everything runs on
this machine -- applicant details never leave it.</p>
<form method="post" action="/triage">
<textarea name="inquiry" rows="9" placeholder="Hi, my name is ... I make $... per month ..."></textarea>
<br><button type="submit">Triage this inquiry</button></form>
{result}
<p class="note">Inquiry triage only, from self-reported information. Not a credit,
eviction, or background check, and not a rental decision.</p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = PAGE.format(result="").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        from urllib.parse import parse_qs

        form = parse_qs(self.rfile.read(length).decode())
        text = (form.get("inquiry") or [""])[0]
        result = triage(text, CRITERIA)
        block = "<h2>Result</h2><pre>" + html.escape(json.dumps(result, indent=2)) + "</pre>"
        body = PAGE.format(result=block).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # keep the console clean
        pass


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--cli":
        with open(sys.argv[2], encoding="utf-8") as f:
            print(json.dumps(triage(f.read(), CRITERIA), indent=2))
    else:
        port = int(os.environ.get("PORT", "8080"))
        print(f"TenantTriage on http://localhost:{port}  (criteria: {CRITERIA_PATH})")
        HTTPServer(("0.0.0.0", port), Handler).serve_forever()
