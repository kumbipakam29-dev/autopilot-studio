"""Offline integrity checks for the versioned agent catalog."""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "agent_registry_v1.json"


class AgentRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with REGISTRY_PATH.open(encoding="utf-8") as handle:
            cls.registry = json.load(handle)

    def test_registry_has_exactly_100_agents(self):
        self.assertEqual(self.registry["agent_count"], 100)
        self.assertEqual(len(self.registry["agents"]), 100)

    def test_agent_ids_are_unique_and_stable_format(self):
        ids = [agent["id"] for agent in self.registry["agents"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [f"APS-{index:03d}" for index in range(1, 101)])

    def test_each_agent_has_independent_versions_and_safe_defaults(self):
        for agent in self.registry["agents"]:
            with self.subTest(agent=agent.get("id")):
                self.assertTrue(agent["name"])
                self.assertTrue(agent["department"])
                self.assertTrue(agent["purpose"])
                self.assertRegex(agent["agent_version"], r"^\d+\.\d+\.\d+$")
                self.assertRegex(agent["prompt_version"], r"^\d+\.\d+\.\d+$")
                self.assertEqual(agent["status"], "planned")
                self.assertEqual(agent["model_profile"], "unassigned")
                self.assertEqual(agent["model_version"], "unassigned")
                self.assertEqual(agent["tool_access"], "deny-by-default")
                self.assertTrue(agent["approval_required"])

    def test_catalog_does_not_claim_agents_are_running(self):
        self.assertIn("not 100 running agents", self.registry["status"])
        self.assertIn("No paid APIs", self.registry["budget_policy"])


if __name__ == "__main__":
    unittest.main()
