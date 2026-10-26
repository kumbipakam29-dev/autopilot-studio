import hashlib
import hmac
import json
import os
import threading
import unittest
from http.client import HTTPConnection
from unittest.mock import patch

from autopilot.integrations.whatsapp_webhook_server import (
    ThreadingHTTPServer,
    WhatsAppWebhookHandler,
)


class WebhookHTTPAdapterTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "WHATSAPP_VERIFY_TOKEN": "verify-secret",
            "META_APP_SECRET": "app-secret",
        })
        self.env.start()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), WhatsAppWebhookHandler)
        self.server.last_drafts = []
        self.server.last_draft_count = 0
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)

    def tearDown(self):
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.env.stop()

    def test_get_challenge_success_and_failure(self):
        self.connection.request("GET", "/webhook?hub.mode=subscribe&hub.verify_token=verify-secret&hub.challenge=12345")
        response = self.connection.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.read(), b"12345")

        self.connection.request("GET", "/webhook?hub.mode=subscribe&hub.verify_token=wrong&hub.challenge=12345")
        response = self.connection.getresponse()
        self.assertEqual(response.status, 403)
        response.read()

    def test_post_rejects_invalid_signature(self):
        body = b'{"object":"whatsapp_business_account"}'
        self.connection.request("POST", "/webhook", body=body, headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=bad",
        })
        response = self.connection.getresponse()
        self.assertEqual(response.status, 401)
        response.read()

    def test_post_accepts_signed_message_and_creates_draft_only(self):
        payload = {"entry": [{"changes": [{"value": {
            "metadata": {"phone_number_id": "test-id"},
            "messages": [{"id": "wamid.test", "from": "919000000000",
                          "type": "text", "text": {"body": "What is your price?"}}]
        }}]}]}
        body = json.dumps(payload).encode()
        signature = "sha256=" + hmac.new(b"app-secret", body, hashlib.sha256).hexdigest()
        self.connection.request("POST", "/webhook", body=body, headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        })
        response = self.connection.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.read(), b"EVENT_RECEIVED")
        self.assertEqual(self.server.last_draft_count, 1)
        self.assertEqual(self.server.last_drafts[0]["status"], "draft_only")


if __name__ == "__main__":
    unittest.main()
