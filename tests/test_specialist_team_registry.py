import copy
import json
import unittest
from pathlib import Path

from scripts.validate_specialist_team_registry import validate_registry


class SpecialistTeamRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "agents" / "specialist_team_registry.json"
        cls.data = json.loads(path.read_text(encoding="utf-8"))

    def test_exactly_45_roles_in_three_departments(self):
        self.assertEqual(self.data["total_agents"], 45)
        self.assertEqual(self.data["departments"], {
            "social_media_specialist": 15,
            "auto_error_handling": 15,
            "cybersecurity_defense": 15,
        })
        self.assertEqual(validate_registry(self.data), [])

    def test_agent_ids_are_unique(self):
        broken = copy.deepcopy(self.data)
        broken["agents"][1]["id"] = broken["agents"][0]["id"]
        self.assertTrue(any("unique" in error for error in validate_registry(broken)))

    def test_external_actions_are_denied_by_default(self):
        broken = copy.deepcopy(self.data)
        broken["agents"][0]["permissions"]["public_publish"] = True
        self.assertTrue(any("public_publish must remain denied" in error for error in validate_registry(broken)))

    def test_cybersecurity_roles_are_defensive_scope_only(self):
        broken = copy.deepcopy(self.data)
        cyber = next(agent for agent in broken["agents"] if agent["department"] == "cybersecurity_defense")
        cyber["safety_profile"] = "unrestricted"
        self.assertTrue(any("authorized defensive scope" in error for error in validate_registry(broken)))

    def test_catalogue_does_not_claim_running_agents(self):
        self.assertTrue(all(agent["registry_status"] == "registered" for agent in self.data["agents"]))
        self.assertTrue(all(agent["execution_status"] == "planned" for agent in self.data["agents"]))
        self.assertTrue(all("not a running worker" in agent["notes"] for agent in self.data["agents"]))


if __name__ == "__main__":
    unittest.main()
