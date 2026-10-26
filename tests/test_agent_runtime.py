import json
import tempfile
import unittest
from pathlib import Path
from agents.runtime import run_task, get_status, load_registry

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.temp.name) / "runs.sqlite3"
        self.registry = Path(__file__).resolve().parents[1] / "agents" / "registry.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_caption_handler_returns_reviewable_draft(self):
        result = run_task("APS-SOCIAL-GROWTH-361", "draft a caption", {"business":"Cafe","offer":"fresh coffee"}, self.registry, self.ledger)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["result"]["requires_human_review"])
        self.assertIn("Cafe", result["result"]["content"])

    def test_unknown_registered_agent_is_blocked(self):
        result = run_task("APS-DESIGN-POD-001", "create design", {}, self.registry, self.ledger)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["error"], "handler_not_implemented")

    def test_sensitive_task_waits_for_approval(self):
        result = run_task("APS-SOCIAL-GROWTH-361", "publish this post now", {}, self.registry, self.ledger)
        self.assertEqual(result["status"], "awaiting_approval")
        self.assertTrue(result["requires_approval"])
        self.assertIsNone(result["result"])

    def test_unknown_id_blocked(self):
        result = run_task("APS-NOT-REAL-999", "test", {}, self.registry, self.ledger)
        self.assertEqual(result["status"], "blocked")

    def test_run_ledger_records_versions_and_status(self):
        result = run_task("APS-SOCIAL-GROWTH-364", "draft reel", {"topic":"coffee"}, self.registry, self.ledger)
        status = get_status(self.ledger)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(status["recent_runs"]), 1)
        self.assertEqual(status["recent_runs"][0]["agent_version"], "1.0.0")

    def test_status_separates_implemented_handlers_from_catalogue(self):
        status = get_status(self.ledger)
        counts = status["registry_counts"]
        registry = load_registry(self.registry)
        self.assertEqual(counts["registered"], len(registry["agents"]))
        self.assertEqual(counts["implemented_handlers"], 5)
        self.assertEqual(
            counts["catalogued_but_unimplemented"],
            counts["registered"] - counts["implemented_handlers"],
        )
        self.assertEqual(counts["implemented_handlers"] + counts["catalogued_but_unimplemented"], counts["registered"])

if __name__ == "__main__":
    unittest.main()
