"""Offline tests for the deterministic specialist capability prototypes."""
import unittest

from agents.specialist_capabilities import (
    CAPABILITIES, approval_gatekeeper, caption_variant_lab, client_brief_structurer,
    content_calendar_architect, local_business_niche_researcher,
    outreach_personalization_drafter, portfolio_spec_work_designer,
    public_source_verifier, rate_evidence_extractor, reel_script_engineer,
    run_capability, scam_signal_triage, task_dependency_mapper,
    version_drift_auditor, workflow_resume_planner, failure_replay_analyst,
)


class SpecialistCapabilityTests(unittest.TestCase):
    def test_all_fifteen_ids_are_runnable_and_return_version(self):
        self.assertEqual(len(CAPABILITIES), 15)
        samples = {
            "APS-SM-01": {"url": "https://example.org", "publisher": "Example", "checked_at": "today", "evidence_summary": "supplied"},
            "APS-SM-02": {"text": "Pay ₹250 per task"},
            "APS-SM-03": {"description": "Pay upfront fee to earn guaranteed income"},
            "APS-SM-04": {"business_type": "cafe", "audience": "locals", "offer": "coffee", "platforms": ["Instagram"]},
            "APS-SM-05": {"offer": "coffee", "audience": "locals"},
            "APS-LG-01": {"tasks": [{"id": "a"}, {"id": "b", "depends_on": ["a"]}]},
            "APS-LG-02": {"action": "publish_post"},
            "APS-LG-03": {"log": "ERROR test failed"},
            "APS-LG-04": {"expected": {"prompt": "1"}, "observed": {"prompt": "2"}},
            "APS-LG-05": {"tasks": [{"id": "a", "status": "pending"}]},
            "APS-CR-01": {"business_type": "cafe", "facts": ["open daily"]},
            "APS-CR-02": {"business_name": "Cafe", "offer": "coffee"},
            "APS-CR-03": {"topic": "coffee"},
            "APS-CR-04": {"business_type": "cafe"},
            "APS-CR-05": {"business_name": "Cafe", "specific_public_fact": "your menu lists breakfast"},
        }
        for agent_id, sample in samples.items():
            with self.subTest(agent_id=agent_id):
                result = run_capability(agent_id, sample)
                self.assertEqual(result["capability_version"], "0.1.0")

    def test_source_checker_does_not_claim_to_fetch_or_verify(self):
        result = public_source_verifier({"url": "https://example.org"})
        self.assertFalse(result["fetched_or_verified_online"])
        self.assertEqual(result["status"], "needs_human_review")

    def test_rate_extractor_preserves_context_and_does_not_verify(self):
        result = rate_evidence_extractor({"text": "The listing says ₹250 per task, subject to approval."})
        self.assertEqual(result["matches"][0]["text"], "₹250 per task")
        self.assertFalse(result["verified_rate"])
        self.assertEqual(rate_evidence_extractor({"text": "No pay listed"})["status"], "rate_not_found_in_supplied_text")

    def test_scam_flags_are_signals_not_verdicts(self):
        result = scam_signal_triage({"description": "Pay upfront fee for guaranteed income"})
        self.assertIn("upfront_payment", result["signals"])
        self.assertFalse(result["fraud_determined"])

    def test_brief_reports_missing_fields(self):
        result = client_brief_structurer({"business_type": "cafe"})
        self.assertEqual(set(result["missing_fields"]), {"audience", "offer", "platforms"})

    def test_calendar_has_seven_days_and_is_not_published(self):
        result = content_calendar_architect({"business_name": "Cafe"})
        self.assertEqual(len(result["calendar"]), 7)
        self.assertTrue(all(day["status"] == "draft_not_published" for day in result["calendar"]))

    def test_reel_script_duration_is_14_to_20_seconds(self):
        result = reel_script_engineer({"topic": "coffee"})
        self.assertGreaterEqual(result["duration_sec"], 14)
        self.assertLessEqual(result["duration_sec"], 20)
        self.assertEqual(result["scenes"][-1]["end_sec"], result["duration_sec"])

    def test_spec_work_is_explicitly_fictional(self):
        result = portfolio_spec_work_designer({})
        self.assertIn("FICTIONAL SPEC WORK", result["label"])
        self.assertFalse(result["real_client_claim"])
        self.assertFalse(result["published"])

    def test_outreach_requires_grounded_fact_and_never_sends(self):
        missing = outreach_personalization_drafter({"business_name": "Cafe"})
        self.assertIsNone(missing["draft"])
        result = outreach_personalization_drafter({"business_name": "Cafe", "specific_public_fact": "menu lists breakfast"})
        self.assertFalse(result["sent"])

    def test_approval_gate_blocks_external_actions(self):
        self.assertEqual(approval_gatekeeper({"action": "publish_post"})["decision"],
                         "blocked_pending_explicit_human_approval")
        self.assertEqual(approval_gatekeeper({"action": "draft_content"})["decision"],
                         "allowed_local_draft_or_analysis")
        self.assertFalse(approval_gatekeeper({"action": "publish_post"})["action_executed"])

    def test_dependency_mapper_detects_unknown_dependency_and_cycle(self):
        unknown = task_dependency_mapper({"tasks": [{"id": "a", "depends_on": ["missing"]}]})
        self.assertIn("unknown dependency missing", unknown["errors"])
        cycle = task_dependency_mapper({"tasks": [{"id": "a", "depends_on": ["b"]}, {"id": "b", "depends_on": ["a"]}]})
        self.assertIn("dependency cycle detected", cycle["errors"])

    def test_version_drift_and_resume_planner(self):
        drift = version_drift_auditor({"expected": {"prompt": "1"}, "observed": {"prompt": "2"}})
        self.assertEqual(drift["status"], "drift_detected")
        plan = workflow_resume_planner({"tasks": [{"id": "a", "status": "completed"}, {"id": "b", "depends_on": ["a"]}]})
        self.assertEqual(plan["ready"], ["b"])
        self.assertFalse(plan["tasks_started"])

    def test_failure_replay_does_not_execute_command(self):
        result = failure_replay_analyst({"log": "Traceback\nAssertionError: failed"})
        self.assertFalse(result["replay_executed"])
        self.assertTrue(result["failure_markers"])

    def test_niche_researcher_uses_supplied_facts_only(self):
        result = local_business_niche_researcher({"facts": ["serves breakfast"]})
        self.assertEqual(result["research_source"], "user_supplied_input_only")
        self.assertIn("serves breakfast", result["provided_facts"])

    def test_caption_variants_are_drafts(self):
        result = caption_variant_lab({"offer": "coffee"})
        self.assertEqual(len(result["drafts"]), 3)
        self.assertEqual(result["status"], "drafts_for_review")

    def test_unknown_agent_is_rejected(self):
        with self.assertRaises(KeyError):
            run_capability("NOPE", {})

    def test_malformed_inputs_are_rejected_where_contract_requires(self):
        with self.assertRaises(TypeError):
            run_capability("APS-SM-01", [])
        self.assertEqual(task_dependency_mapper({"tasks": "bad"})["status"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
