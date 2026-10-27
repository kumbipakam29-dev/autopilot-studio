"""Tests for the deterministic, no-network specialist runner."""
import json
import tempfile
import unittest
from pathlib import Path

from agents.specialist_runner import (
    append_log,
    grade_opportunity,
    load_config,
    run_task,
    validate_catalog,
)


class SpecialistRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()

    def test_catalog_validation_passes_for_current_registry(self):
        result = validate_catalog({"expected_count": 15}, self.config)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["checked_agents"], 15)
        self.assertEqual(result["errors"], [])

    def test_catalog_validation_detects_bad_expected_count(self):
        result = validate_catalog({"expected_count": 14}, self.config)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["errors"])

    def test_catalog_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            altered = json.loads(json.dumps(self.config))
            altered["agents"][1]["id"] = altered["agents"][0]["id"]
            path.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unique"):
                load_config(path)

    def test_opportunity_missing_evidence_needs_review(self):
        result = grade_opportunity({"official_source_url": "https://example.org"}, self.config)
        self.assertEqual(result["status"], "needs_human_review")
        self.assertIn("payout_details", result["missing_evidence"])

    def test_opportunity_complete_fields_only_ready_for_human_review(self):
        payload = {
            "official_source_url": "https://example.org",
            "country_eligibility": "India eligibility shown on official page",
            "task_rate_unit": "₹100 per accepted task, official page says so",
            "acceptance_criteria": "Submit a labelled 10-row sample; reviewed by client",
            "payout_details": "Bank transfer after acceptance, per official terms",
        }
        result = grade_opportunity(payload, self.config)
        self.assertEqual(result["status"], "ready_for_human_review")
        self.assertEqual(result["missing_evidence"], [])

    def test_unverified_fields_do_not_pass(self):
        payload = {
            "official_source_url": "http://example.org",
            "country_eligibility": "unknown",
            "task_rate_unit": "TBD",
            "acceptance_criteria": "unverified",
            "payout_details": "n/a",
        }
        result = grade_opportunity(payload, self.config)
        self.assertEqual(result["status"], "needs_human_review")
        self.assertTrue(result["missing_evidence"])

    def test_run_record_never_claims_automatic_learning(self):
        record = run_task("validate_agent_catalog", {"expected_count": 15}, self.config)
        self.assertEqual(record["result"]["status"], "passed")
        self.assertFalse(record["auto_learned"])
        self.assertEqual(record["learning_status"], "evaluation_record_only")
        self.assertEqual(record["model_version"], "unassigned")

    def test_unsupported_task_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            run_task("send_outreach", {}, self.config)

    def test_log_appends_jsonl_without_touching_repo_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runs.jsonl"
            record = run_task("validate_agent_catalog", {}, self.config)
            append_log(record, path)
            append_log(record, path)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])["task_type"], "validate_agent_catalog")


if __name__ == "__main__":
    unittest.main()
