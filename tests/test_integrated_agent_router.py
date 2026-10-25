import unittest
from pathlib import Path

from agents.integrated_agent_router import build_agent_package


class IntegratedAgentRouterTests(unittest.TestCase):
    def setUp(self):
        self.catalog_path = Path(__file__).resolve().parents[1] / "agents" / "model_profiles.json"

    def test_deterministic_agent_draft_uses_versioned_rules_profile(self):
        package = build_agent_package(
            "JSON Validator", "Validate structured data", ["validation"],
            "validate JSON", {"ram_gb": 2}, {"rules-engine"},
            catalog_path=self.catalog_path,
        )
        self.assertEqual(package["package_status"], "draft_ready_for_human_review")
        self.assertEqual(package["model_route"]["selected_profile"], "rules-engine")
        self.assertEqual(package["model_route"]["profile_version"], "1.0.0")
        self.assertFalse(package["execution_performed"])
        self.assertFalse(package["external_actions_performed"])
        self.assertEqual(package["agent_spec"]["status"], "draft_requires_evaluation")

    def test_uninstalled_local_model_is_setup_required_not_ready(self):
        package = build_agent_package(
            "Research Helper", "Summarize public reports", ["summarization"],
            "summarize this report", {"ram_gb": 16, "vram_gb": 0}, {"rules-engine"},
            catalog_path=self.catalog_path,
        )
        self.assertEqual(package["package_status"], "draft_blocked_on_model_setup_or_task_support")
        self.assertEqual(package["model_route"]["route_status"], "setup_required")
        self.assertFalse(package["model_route"]["execution_ready"])

    def test_unknown_task_does_not_fall_back_to_remote(self):
        package = build_agent_package(
            "Mystery", "Do an unspecified task", ["research"], "do something novel",
            {"ram_gb": 64, "vram_gb": 24}, {"rules-engine"}, allow_remote=True,
            catalog_path=self.catalog_path,
        )
        self.assertEqual(package["model_route"]["route_status"], "unsupported")
        self.assertFalse(package["model_route"]["execution_ready"])
        self.assertFalse(package["model_route"].get("remote_used", False))

    def test_only_explicitly_verified_profiles_can_be_marked_ready(self):
        package = build_agent_package(
            "Coder", "Draft code", ["coding"], "write code for a script",
            {"ram_gb": 32, "vram_gb": 12}, {"rules-engine"},
            catalog_path=self.catalog_path,
        )
        self.assertEqual(package["model_route"]["route_status"], "setup_required")
        self.assertFalse(package["execution_performed"])

    def test_empty_task_is_rejected(self):
        with self.assertRaises(ValueError):
            build_agent_package("A", "Purpose", ["text"], "  ", catalog_path=self.catalog_path)


if __name__ == "__main__":
    unittest.main()
