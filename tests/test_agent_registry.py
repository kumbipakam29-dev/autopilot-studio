import json
import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_agent_registry", ROOT / "scripts" / "validate_agent_registry.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class RegistryTests(unittest.TestCase):
    def test_registry_is_valid(self):
        data = json.loads((ROOT / "agents" / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(MOD.validate(data), [])

    def test_all_ids_unique(self):
        data = MOD.load()
        ids = [a["id"] for a in data["agents"]]
        self.assertEqual(len(ids), 500)
        self.assertEqual(len(set(ids)), 500)

    def test_registry_does_not_claim_agents_running(self):
        data = MOD.load()
        self.assertTrue(all(a["execution_status"] == "planned" for a in data["agents"]))

    def test_all_150_ideas_covered(self):
        data = MOD.load()
        idea_numbers = {a["idea_number"] for a in data["agents"] if a["department"] != "seasonal_variations"}
        self.assertEqual(idea_numbers, set(range(1, 151)))

if __name__ == "__main__":
    unittest.main()
