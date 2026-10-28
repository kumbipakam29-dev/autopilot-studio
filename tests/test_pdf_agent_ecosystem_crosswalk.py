"""Integrity tests for the two PDF-derived agent role mappings."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "config" / "pdf_agent_ecosystem_crosswalk_v1.json"
ALLOWED_STATUSES = {"partial", "not_implemented"}


class PdfAgentCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CROSSWALK.read_text(encoding="utf-8"))

    def test_maps_ten_distinct_roles(self):
        roles = self.data["roles"]
        self.assertEqual(len(roles), 10)
        names = [role["pdf_role"] for role in roles]
        self.assertEqual(len(names), len(set(names)))

    def test_each_mapped_path_exists(self):
        for role in self.data["roles"]:
            for relative_path in role["implementation_paths"]:
                with self.subTest(role=role["pdf_role"], path=relative_path):
                    self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_statuses_are_conservative_and_explicit(self):
        for role in self.data["roles"]:
            with self.subTest(role=role["pdf_role"]):
                self.assertIn(role["status"], ALLOWED_STATUSES)
                self.assertTrue(role["current_behavior"].strip())
                self.assertTrue(role["gap"].strip())
                self.assertTrue(role["safe_next_step"].strip())
        roles = {role["pdf_role"]: role for role in self.data["roles"]}
        self.assertEqual(roles["Coder"]["status"], "not_implemented")
        self.assertFalse(self.data["claim_of_running_model_backed_agents"])

    def test_no_framework_install_or_paid_api_is_claimed(self):
        self.assertIn("not installed or activated", self.data["framework_policy"])
        self.assertTrue(self.data["budget_policy"].startswith("No new dependencies"))


if __name__ == "__main__":
    unittest.main()
