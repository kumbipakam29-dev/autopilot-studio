import json
import math
import tempfile
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

    def test_boolean_memory_values_are_rejected_as_invalid_capabilities(self):
        for device in ({"ram_gb": True}, {"ram_gb": 16, "vram_gb": False}):
            result = recommend_profile("reasoning", device, {"rules-engine"}, self.catalog_path)
            self.assertEqual(result["route_status"], "device_incompatible_or_unknown")
            self.assertFalse(result["execution_ready"])

    def test_non_finite_memory_values_are_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            result = recommend_profile("reasoning", {"ram_gb": value, "vram_gb": 0}, {"rules-engine"}, self.catalog_path)
            self.assertEqual(result["route_status"], "device_incompatible_or_unknown")
            self.assertFalse(result["execution_ready"])

    def test_non_dictionary_device_is_rejected(self):
        for invalid_device in ([], ["ram", 16], ""):
            with self.subTest(device=invalid_device):
                with self.assertRaises(ValueError):
                    recommend_profile("reasoning", invalid_device, {"rules-engine"}, self.catalog_path)

    def test_none_device_means_unknown_capabilities_not_invalid_input(self):
        result = recommend_profile("reasoning", None, {"rules-engine"}, self.catalog_path)
        self.assertEqual(result["route_status"], "device_incompatible_or_unknown")
        self.assertFalse(result["execution_ready"])

    def test_invalid_installed_profile_declarations_are_rejected(self):
        for installed in ("rules-engine", [{"id": "rules-engine"}], {None}, {""}):
            with self.subTest(installed=installed), self.assertRaises(ValueError):
                recommend_profile("structured", {"ram_gb": 2}, installed, self.catalog_path)

    def test_catalog_rejects_boolean_resource_threshold(self):
        catalog = {
            "schema_version": "test",
            "profiles": [{
                "id": "bad-profile", "version": "1", "kind": "local_llm",
                "tasks": ["reasoning"], "min_ram_gb": True, "min_vram_gb": 0
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profiles(path)

    def test_catalog_rejects_non_object_root_and_non_object_profiles(self):
        invalid_catalogs = (
            [],
            "not a catalog",
            {"profiles": ["not a profile"]},
            {"profiles": [None]},
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            for catalog in invalid_catalogs:
                with self.subTest(catalog=catalog):
                    path.write_text(json.dumps(catalog), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_profiles(path)

    def test_catalog_rejects_empty_version_or_kind(self):
        for key in ("version", "kind"):
            catalog = {
                "schema_version": "test",
                "profiles": [{
                    "id": "bad-profile", "version": "1", "kind": "local_llm",
                    "tasks": ["reasoning"], "min_ram_gb": 8, "min_vram_gb": 0
                }]
            }
            catalog["profiles"][0][key] = "  "
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "catalog.json"
                path.write_text(json.dumps(catalog), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_profiles(path)

    def test_catalog_rejects_unhashable_or_empty_profile_ids_cleanly(self):
        for profile_id in ([], {}, "", "   ", None):
            catalog = {
                "profiles": [{
                    "id": profile_id, "version": "1", "kind": "local_llm",
                    "tasks": ["reasoning"], "min_ram_gb": 8, "min_vram_gb": 0
                }]
            }
            with self.subTest(profile_id=profile_id), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "catalog.json"
                path.write_text(json.dumps(catalog), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_profiles(path)


if __name__ == "__main__":
    unittest.main()
