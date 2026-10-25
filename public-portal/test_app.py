import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
import app as portal


class DraftTaskTests(unittest.TestCase):
    def test_caption_task_returns_draft(self):
        result = portal._draft("caption", "a local cafe weekend special")
        self.assertIn("local cafe weekend special", result)
        self.assertIn("#SmallBusiness", result)

    def test_reel_task_has_requested_timing(self):
        result = portal._draft("reel_script", "home cleaning service")
        self.assertIn("14–20 second Reel concept", result)
        self.assertIn("0–3s", result)
        self.assertIn("15–20s", result)

    def test_calendar_states_not_published(self):
        result = portal._draft("content_calendar", "a bakery")
        self.assertIn("Day 7", result)
        self.assertIn("not published", result)

    def test_unknown_task_is_not_executed(self):
        self.assertIsNone(portal._draft("shell", "run a command"))

    def test_sensitive_actions_are_flagged(self):
        self.assertRegex("please publish this", portal.APPROVAL_TERMS)
        self.assertRegex("send message to customer", portal.APPROVAL_TERMS)
        self.assertRegex("delete the repository", portal.APPROVAL_TERMS)
        self.assertRegex("deploy this website", portal.APPROVAL_TERMS)

    def test_registry_lists_supported_draft_agents(self):
        registry = portal.agents()
        self.assertEqual(registry["count"], 4)
        self.assertEqual({agent["task"] for agent in registry["agents"]},
                         {"caption", "reel_script", "content_calendar", "public_summary"})

    def test_registry_does_not_claim_external_actions(self):
        self.assertTrue(all(agent["external_actions"] is False for agent in portal.AGENT_REGISTRY))
        public_research = next(agent for agent in portal.AGENT_REGISTRY if agent["task"] == "public_summary")
        self.assertEqual(public_research["status"], "limited")

    def test_secret_and_contact_redaction(self):
        cleaned = portal._redact("send email to alice@example.com; api_key=supersecret; phone +91 98765 43210")
        self.assertNotIn("alice@example.com", cleaned)
        self.assertNotIn("supersecret", cleaned)
        self.assertNotIn("98765 43210", cleaned)


class PortalApiTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.old_db_path = portal.DB_PATH
        portal.DB_PATH = Path(self.tempdir.name) / "approvals.sqlite3"
        portal._request_times.clear()
        self.client = TestClient(portal.app)

    def tearDown(self):
        portal.DB_PATH = self.old_db_path
        self.tempdir.cleanup()

    def test_homepage_serves_agent_dashboard(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Agent status", response.text)
        self.assertIn("refresh-agents", response.text)

    def test_unsupported_auto_request_is_rejected(self):
        response = self.client.post("/api/chat", json={"message": "Please explain an unrelated task", "task": "auto"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "unsupported")
        self.assertIsNone(response.json()["result"])

    def test_health_endpoint_reports_prototype_mode(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "prototype-no-external-actions")

    def test_agent_registry_endpoint(self):
        response = self.client.get("/api/agents")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 4)

    def test_caption_request_returns_draft(self):
        response = self.client.post("/api/chat", json={"message": "Create an Instagram caption for a bakery", "task": "auto"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")
        self.assertIn("Draft caption", response.json()["result"])

    def test_sensitive_request_is_queued_and_not_executed(self):
        response = self.client.post("/api/chat", json={"message": "Please publish this to Instagram", "task": "auto"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "needs_approval")
        self.assertIsNone(body["result"])
        with patch.dict(os.environ, {"AUTOPILOT_APPROVAL_TOKEN": "test-secret"}):
            queue = self.client.get("/api/approvals", headers={"X-Approval-Token": "test-secret"})
        self.assertEqual(queue.status_code, 200)
        self.assertEqual(queue.json()["count"], 1)
        self.assertEqual(queue.json()["approvals"][0]["task_id"], body["task_id"])

    def test_approval_admin_requires_configured_token(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get("/api/approvals")
        self.assertEqual(response.status_code, 503)

    def test_approval_admin_rejects_wrong_token(self):
        with patch.dict(os.environ, {"AUTOPILOT_APPROVAL_TOKEN": "right-secret"}):
            response = self.client.get("/api/approvals", headers={"X-Approval-Token": "wrong-secret"})
        self.assertEqual(response.status_code, 401)

    def test_review_decision_is_recorded_but_never_executes(self):
        with patch.dict(os.environ, {"AUTOPILOT_APPROVAL_TOKEN": "test-secret"}):
            created = self.client.post("/api/chat", json={"message": "Send this email to the client"})
            task_id = created.json()["task_id"]
            response = self.client.post(
                f"/api/approvals/{task_id}/decision",
                headers={"X-Approval-Token": "test-secret"},
                json={"decision": "approved_for_manual_review"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json()["executed"])
            self.assertEqual(response.json()["status"], "approved_for_manual_review")
            again = self.client.post(
                f"/api/approvals/{task_id}/decision",
                headers={"X-Approval-Token": "test-secret"},
                json={"decision": "rejected"},
            )
            self.assertEqual(again.status_code, 409)

    def test_oversized_message_is_rejected(self):
        response = self.client.post("/api/chat", json={"message": "x" * 2001, "task": "caption"})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
