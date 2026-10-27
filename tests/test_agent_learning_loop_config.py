"""Offline structural tests for the 15-specialist learning-loop configuration."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "agent_learning_loop_v1.json"


class SpecialistLearningLoopConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_exactly_15_unique_specialists(self):
        agents = self.config["agents"]
        self.assertEqual(len(agents), 15)
        ids = [agent["id"] for agent in agents]
        self.assertEqual(len(ids), len(set(ids)))
        names = [agent["name"] for agent in agents]
        self.assertEqual(len(names), len(set(names)))

    def test_each_specialist_has_bounded_contract(self):
        required = {
            "id", "name", "department", "specialized_task", "workflow",
            "expected_output", "agent_version", "prompt_version", "status",
            "evaluation_status", "tool_policy", "approval_required",
            "success_metrics", "failure_labels", "learning_rule",
        }
        for agent in self.config["agents"]:
            with self.subTest(agent=agent.get("id")):
                self.assertTrue(required.issubset(agent))
                self.assertEqual(agent["status"], "planned")
                self.assertEqual(agent["evaluation_status"], "not-run")
                self.assertEqual(agent["tool_policy"], "deny-by-default")
                self.assertIs(agent["approval_required"], True)
                self.assertTrue(agent["success_metrics"])
                self.assertTrue(agent["failure_labels"])

    def test_rubric_weights_total_100(self):
        weights = self.config["evaluation"]["dimensions"]
        self.assertEqual(sum(weights.values()), 100)
        self.assertGreaterEqual(self.config["evaluation"]["pass_threshold"], 0)
        self.assertLessEqual(self.config["evaluation"]["pass_threshold"], 100)

    def test_hard_fail_and_approval_gates_exist(self):
        hard_fail = self.config["evaluation"]["hard_fail"]
        gates = self.config["approval_gates"]
        self.assertIn("fabricated source or result", hard_fail)
        self.assertIn("unauthorized external action", hard_fail)
        self.assertIn("external messages", gates)
        self.assertIn("repository merge", gates)
        self.assertIn("payments/purchases", gates)

    def test_budget_and_model_status_are_explicit(self):
        self.assertIn("₹0", self.config["budget_policy"])
        self.assertIn("not evidence", self.config["status"])
        for agent in self.config["agents"]:
            self.assertEqual(agent["model_profile"], "unassigned")
            self.assertIn("not", agent["status"])


if __name__ == "__main__":
    unittest.main()
