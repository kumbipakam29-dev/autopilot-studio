"""Regression tests for the safe office orchestrator."""
import unittest

from agents.office_orchestrator import build_run_report, execute_job


class OfficeOrchestratorTests(unittest.TestCase):
    def test_office_audit_runs_catalog_checks(self):
        result = execute_job({"job_type": "office_audit", "payload": {"expected_count": 15}})
        self.assertEqual(result["status"], "completed_for_review")
        self.assertEqual(result["result"]["checked_agents"], 15)
        self.assertFalse(result["model_inference_used"])

    def test_client_pack_is_review_only_and_not_published(self):
        result = execute_job({
            "job_type": "client_acquisition_pack",
            "payload": {
                "business_name": "Demo Cafe",
                "business_type": "cafe",
                "audience": "nearby customers",
                "offer": "coffee",
                "specific_public_fact": "example fact supplied for test",
            },
        })
        self.assertEqual(result["status"], "completed_for_review")
        self.assertFalse(result["external_side_effects"])
        self.assertFalse(result["result"]["safety"]["outreach_sent"])
        self.assertFalse(result["result"]["safety"]["content_published"])

    def test_browser_and_publishing_are_explicitly_blocked(self):
        for action in ("browse_web", "send_outreach", "publish_content", "modify_repository", "make_payment"):
            with self.subTest(action=action):
                result = execute_job({"job_type": action, "payload": {}})
                self.assertEqual(result["status"], "blocked")
                self.assertTrue(result["approval_required"])

    def test_batch_continues_after_bad_job_and_reports_counts(self):
        report = build_run_report([
            {"job_type": "office_audit", "payload": {}},
            {"job_type": "not_a_real_job", "payload": {}},
            {"job_type": "browse_web", "payload": {}},
        ])
        self.assertEqual(report["summary"], {
            "total": 3, "completed_for_review": 1, "blocked": 1, "failed": 1
        })
        self.assertEqual(len(report["records"]), 3)

    def test_unknown_specialist_is_reported_as_failed(self):
        report = build_run_report([{
            "job_type": "specialist_task",
            "payload": {"agent_id": "DOES-NOT-EXIST", "input": {}},
        }])
        self.assertEqual(report["summary"]["failed"], 1)


if __name__ == "__main__":
    unittest.main()
