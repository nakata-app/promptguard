"""Minimal HTTP server for promptguard — no extra dependencies.

Usage:
    python -m promptguard serve [--port 8765] [--host 127.0.0.1]

POST /check
    Body: {"text": "user input here"}
    Response: {"action": "PASS"|"WARN"|"BLOCK", "risk_score": 0.0-1.0,
               "matched_rules": [...], "classifier_score": null|float}

GET /health
    Response: {"status": "ok"}

The server is intentionally single-threaded and loopback-only by default.
It is designed to run as a sidecar on localhost — not a public endpoint.
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from promptguard.guard import PromptGuard

_guard: PromptGuard | None = None


def _get_guard() -> PromptGuard:
    global _guard
    if _guard is None:
        _guard = PromptGuard()
    return _guard


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # silence access log — callers see nothing on clean requests

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/check":
            self._json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
            text: str = body["text"]
        except Exception:
            self._json(400, {"error": "invalid JSON or missing 'text'"})
            return

        verdict = _get_guard().check(text)
        self._json(
            200,
            {
                "action": verdict.suggested_action.value,
                "risk_score": verdict.risk_score,
                "matched_rules": verdict.matched_rules,
                "classifier_score": verdict.classifier_score,
            },
        )

    def _json(self, code: int, data: dict[str, Any]) -> None:
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = HTTPServer((host, port), _Handler)
    print(f"[promptguard] listening on {host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[promptguard] shutting down", flush=True)
        sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(prog="promptguard serve")
    parser.add_argument("command", choices=["serve"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(host=args.host, port=args.port)
