import hashlib
import hmac
import unittest
from unittest.mock import patch

from autopilot.integrations.whatsapp_cloud import (
    build_reply_draft,
    extract_incoming_messages,
    verify_signature,
    verify_webhook_challenge,
)
from autopilot.plugins.registry import Plugin, PluginRegistry


class WhatsAppWebhookTests(unittest.TestCase):
    def test_challenge_requires_matching_token(self):
        with patch.dict("os.environ", {"WHATSAPP_VERIFY_TOKEN": "test-secret"}):
            self.assertEqual(verify_webhook_challenge("subscribe", "test-secret", "abc"), "abc")
            self.assertIsNone(verify_webhook_challenge("subscribe", "wrong", "abc"))
            self.assertIsNone(verify_webhook_challenge("other", "test-secret", "abc"))

    def test_signature(self):
        body = b'{"hello":"world"}'
        secret = "app-secret"
        signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        self.assertTrue(verify_signature(body, signature, secret))
        self.assertFalse(verify_signature(body, "sha256=bad", secret))

    def test_extract_and_triage(self):
        payload = {"entry": [{"changes": [{"value": {
            "metadata": {"phone_number_id": "123"},
            "messages": [{"id": "wamid.1", "from": "919999999999",
                          "type": "text", "text": {"body": "What is your price?"}}]
        }}]}]}
        messages = extract_incoming_messages(payload)
        self.assertEqual(messages[0]["message_id"], "wamid.1")
        draft = build_reply_draft(messages[0])
        self.assertEqual(draft["category"], "pricing")
        self.assertEqual(draft["status"], "draft_only")


class PluginRegistryTests(unittest.TestCase):
    def test_requires_approval_before_dispatch(self):
        registry = PluginRegistry()
        registry.register(Plugin("demo", "1.0", "test", lambda value: value))
        with self.assertRaises(PermissionError):
            registry.dispatch("demo", value="ok")
        self.assertEqual(registry.dispatch("demo", approved=True, value="ok"), "ok")

    def test_duplicate_plugin_rejected(self):
        registry = PluginRegistry()
        registry.register(Plugin("demo", "1.0", "test", lambda: None))
        with self.assertRaises(ValueError):
            registry.register(Plugin("DEMO", "1.0", "duplicate", lambda: None))


if __name__ == "__main__":
    unittest.main()
