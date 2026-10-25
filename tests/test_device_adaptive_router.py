import unittest
from pathlib import Path

from agents.device_adaptive_router import recommend_profile, load_profiles


class DeviceAdaptiveRouterTests(unittest.TestCase):
    def setUp(self):
        self.catalog_path = Path(__file__).resolve().parents[1] / "agents" / "model_profiles.json"

    def test_catalog_has_unique_profiles(self):
        catalog = load_profiles(self.catalog_path)
        ids = [profile["id"] for profile in catalog["profiles"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_deterministic_task_uses_available_rules_engine(self):
        result = recommend_profile("structured", {"ram_gb": 2}, {"rules-engine"}, self.catalog_path)
        self.assertEqual(result["route_status"], "ready")
        self.assertEqual(result["selected_profile"], "rules-engine")
        self.assertTrue(result["execution_ready"])
        self.assertFalse(result["remote_used"])

    def test_reasoning_on_low_memory_device_does_not_claim_model_is_running(self):
        result = recommend_profile("reasoning", {"ram_gb": 4, "vram_gb": 0}, {"rules-engine"}, self.catalog_path)
        self.assertEqual(result["route_status"], "device_incompatible_or_unknown")
        self.assertFalse(result["execution_ready"])

    def test_compatible_but_uninstalled_local_model_needs_setup(self):
        result = recommend_profile("reasoning", {"ram_gb": 24, "vram_gb": 12}, {"rules-engine"}, self.catalog_path)
        self.assertEqual(result["route_status"], "setup_required")
        self.assertEqual(result["selected_profile"], "local-llm-medium-q4")
        self.assertFalse(result["execution_ready"])
        self.assertFalse(result["remote_used"])

    def test_installed_local_model_can_be_selected_after_verified_setup(self):
        result = recommend_profile("reasoning", {"ram_gb": 24, "vram_gb": 12}, {"rules-engine", "local-llm-medium-q4"}, self.catalog_path)
        self.assertEqual(result["route_status"], "ready")
        self.assertEqual(result["selected_profile"], "local-llm-medium-q4")
        self.assertTrue(result["execution_ready"])

    def test_unknown_task_is_not_silently_routed_to_remote_api(self):
        result = recommend_profile("unknown_task", {"ram_gb": 32, "vram_gb": 24}, {"rules-engine"}, self.catalog_path, allow_remote=False)
        self.assertEqual(result["route_status"], "unsupported")
        self.assertFalse(result["execution_ready"])
        self.assertIsNone(result["selected_profile"])

    def test_missing_hardware_details_does_not_assume_large_model_fits(self):
        result = recommend_profile("reasoning", {}, {"rules-engine"}, self.catalog_path)
        self.assertEqual(result["route_status"], "device_incompatible_or_unknown")
        self.assertFalse(result["execution_ready"])


if __name__ == "__main__":
    unittest.main()
