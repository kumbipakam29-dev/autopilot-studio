"""Dependency-free primitives for Meta WhatsApp Cloud API webhooks.

This is a safe integration foundation, not a live bot. Deploy behind HTTPS,
configure the callback in Meta, and supply secrets as environment variables.
Never commit access tokens or verification tokens.
"""
from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any


def verify_webhook_challenge(mode: str, token: str, challenge: str) -> str | None:
    """Return the challenge only when Meta's subscription verification matches."""
    expected = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    if mode == "subscribe" and expected and hmac.compare_digest(token, expected):
        return challenge
    return None


def verify_signature(raw_body: bytes, signature_header: str, app_secret: str | None = None) -> bool:
    """Validate X-Hub-Signature-256 using the Meta app secret."""
    secret = app_secret or os.getenv("META_APP_SECRET", "")
    if not secret or not signature_header.startswith("sha256="):
        return False
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest("sha256=" + digest, signature_header)


def extract_incoming_messages(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Extract text messages from a Meta webhook payload; ignore status events."""
    found: list[dict[str, str]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value") or {}
            for message in value.get("messages", []):
                text_body = ((message.get("text") or {}).get("body") or "").strip()
                found.append({
                    "message_id": str(message.get("id", "")),
                    "from": str(message.get("from", "")),
                    "type": str(message.get("type", "")),
                    "text": text_body,
                    "phone_number_id": str((value.get("metadata") or {}).get("phone_number_id", "")),
                })
    return found


def build_reply_draft(message: dict[str, str]) -> dict[str, str]:
    """Create a safe triage record; sending is intentionally not implemented."""
    body = message.get("text", "")
    lowered = body.lower()
    if any(word in lowered for word in ("price", "cost", "rate", "કિંમત", "कीमत")):
        category = "pricing"
    elif any(word in lowered for word in ("order", "buy", "purchase", "payment", "ઓર્ડર", "ऑर्डर")):
        category = "sales"
    elif any(word in lowered for word in ("help", "problem", "issue", "refund", "મદદ", "मदद")):
        category = "support"
    else:
        category = "general"
    return {
        "to": message.get("from", ""),
        "category": category,
        "draft": "Thanks for contacting AutoPilot Digital Studio. Please share what you need, and we’ll guide you to the right service.",
        "status": "draft_only",
    }
