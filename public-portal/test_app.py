import unittest

from fastapi.testclient import TestClient

from app import AGENT_REGISTRY, APPROVAL_TERMS, _draft, agents, app


class DraftTaskTests(unittest.TestCase):
    def test_caption_task_returns_draft(self):
        result = _draft("caption", "a local cafe weekend special")
        self.assertIn("local cafe weekend special", result)
        self.assertIn("#SmallBusiness", result)

    def test_reel_task_has_requested_timing(self):
        result = _draft("reel_script", "home cleaning service")
        self.assertIn("14–20 second Reel concept", result)
        self.assertIn("0–3s", result)
        self.assertIn("15–20s", result)

    def test_calendar_states_not_published(self):
        result = _draft("content_calendar", "a bakery")
        self.assertIn("Day 7", result)
        self.assertIn("not published", result)

    def test_unknown_task_is_not_executed(self):
        self.assertIsNone(_draft("shell", "run a command"))

    def test_sensitive_actions_are_flagged(self):
        self.assertRegex("please publish this", APPROVAL_TERMS)
        self.assertRegex("send message to customer", APPROVAL_TERMS)
        self.assertRegex("delete the repository", APPROVAL_TERMS)

    def test_registry_lists_supported_draft_agents(self):
        registry = agents()
        self.assertEqual(registry["count"], 4)
        task_ids = {agent["task"] for agent in registry["agents"]}
        self.assertEqual(
            task_ids,
            {"caption", "reel_script", "content_calendar", "public_summary"},
        )

    def test_registry_does_not_claim_external_actions(self):
        self.assertTrue(all(agent["external_actions"] is False for agent in AGENT_REGISTRY))
        public_research = next(agent for agent in AGENT_REGISTRY if agent["task"] == "public_summary")
        self.assertEqual(public_research["status"], "limited")

    def test_normal_draft_request_is_not_sensitive(self):
        self.assertIsNone(APPROVAL_TERMS.search("write a caption for a bakery"))


class PortalApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint_reports_prototype_mode(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "prototype-no-external-actions")

    def test_agent_registry_endpoint(self):
        response = self.client.get("/api/agents")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 4)

    def test_caption_request_returns_draft(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "Create an Instagram caption for a bakery", "task": "auto"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")
        self.assertIn("Draft caption", response.json()["result"])

    def test_sensitive_request_is_not_executed(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "Please publish this to Instagram", "task": "auto"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "needs_approval")
        self.assertIsNone(response.json()["result"])

    def test_oversized_message_is_rejected(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "x" * 2001, "task": "caption"},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
