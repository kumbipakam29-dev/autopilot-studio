"""Minimal stdlib HTTP adapter for the AutoPilot WhatsApp webhook foundation.

Run with: python -m autopilot.integrations.whatsapp_webhook_server
For production, place behind a public HTTPS reverse proxy/host. This adapter
only validates inbound events and creates in-memory draft records; it never
sends messages and does not persist customer content.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from autopilot.integrations.whatsapp_cloud import (
    build_reply_draft,
    extract_incoming_messages,
    verify_signature,
    verify_webhook_challenge,
)


class WhatsAppWebhookHandler(BaseHTTPRequestHandler):
    server_version = "AutoPilotWhatsAppWebhook/0.1"

    def _respond(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/webhook":
            self._respond(404, b"not found")
            return
        query = parse_qs(parsed.query)
        mode = (query.get("hub.mode") or [""])[0]
        token = (query.get("hub.verify_token") or [""])[0]
        challenge = (query.get("hub.challenge") or [""])[0]
        verified = verify_webhook_challenge(mode, token, challenge)
        if verified is None:
            self._respond(403, b"verification failed")
            return
        self._respond(200, verified.encode("utf-8"))

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/webhook":
            self._respond(404, b"not found")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._respond(400, b"invalid content length")
            return
        if length <= 0 or length > 1_000_000:
            self._respond(413 if length > 1_000_000 else 400, b"invalid body size")
            return
        raw = self.rfile.read(length)
        signature = self.headers.get("X-Hub-Signature-256", "")
        if not verify_signature(raw, signature):
            self._respond(401, b"invalid signature")
            return
        try:
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON object required")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            self._respond(400, b"invalid JSON")
            return

        # Do not log message text or phone numbers. This minimal adapter is
        # intentionally in-memory; a durable store and retention policy are
        # separate implementation tasks.
        drafts = [build_reply_draft(item) for item in extract_incoming_messages(payload)]
        self.server.last_draft_count = len(drafts)
        self.server.last_drafts = drafts
        self._respond(200, b"EVENT_RECEIVED")

    def log_message(self, fmt: str, *args: object) -> None:
        # Avoid default request logging, which can leak URL query secrets.
        return


def main() -> None:
    host = os.getenv("AUTOPILOT_WEBHOOK_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("AUTOPILOT_WEBHOOK_PORT", "8080")))
    httpd = ThreadingHTTPServer((host, port), WhatsAppWebhookHandler)
    httpd.last_drafts = []
    httpd.last_draft_count = 0
    print(f"AutoPilot WhatsApp webhook listening on {host}:{port}; endpoint /webhook")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
