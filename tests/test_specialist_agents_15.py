"""Offline integrity tests for the 15 specialized agent specifications."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "specialist_agents_15_v1.json"

class SpecialistAgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PATH.read_text(encoding="utf-8"))

    def test_exactly_fifteen_agents_in_three_framework_groups(self):
        agents = self.data["agents"]
        self.assertEqual(self.data["agent_count"], 15)
        self.assertEqual(len(agents), 15)
        self.assertEqual({a["upstream_framework"] for a in agents}, {"smolagents", "LangGraph", "CrewAI"})
        for framework in {"smolagents", "LangGraph", "CrewAI"}:
            self.assertEqual(sum(a["upstream_framework"] == framework for a in agents), 5)

    def test_unique_ids_and_capabilities(self):
        agents = self.data["agents"]
        self.assertEqual(len({a["id"] for a in agents}), 15)
        self.assertEqual(len({a["purpose"] for a in agents}), 15)
        self.assertEqual(len({a["output_contract"] for a in agents}), 15)

    def test_safe_defaults_and_independent_versions(self):
        for agent in self.data["agents"]:
            with self.subTest(agent=agent["id"]):
                for version in (agent["agent_version"], agent["prompt_version"]):
                    parts = version.split(".")
                    self.assertEqual(len(parts), 3)
                    self.assertTrue(all(part.isdigit() for part in parts))
                self.assertEqual(agent["model_profile"], "unassigned")
                self.assertEqual(agent["model_version"], "unassigned")
                self.assertEqual(agent["status"], "offline-prototype-implemented")
                self.assertEqual(agent["implementation_path"], "agents/specialist_capabilities.py")
                self.assertEqual(agent["capability_version"], "0.1.0")
                self.assertEqual(agent["evaluation_status"], "tests-authored-ci-not-confirmed")
                self.assertTrue(agent["approval_required"])
                self.assertIn("deny-by-default", agent["tool_access"])

    def test_frameworks_are_pattern_study_not_claimed_as_installed(self):
        self.assertIn("not 15 running model-backed agents", self.data["status"])
        for framework in self.data["frameworks"]:
            self.assertIn("no upstream package installed", framework["adoption_mode"])

if __name__ == "__main__":
    unittest.main()
