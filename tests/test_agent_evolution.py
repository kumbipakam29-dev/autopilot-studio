import unittest
from agents.agent_evolution import bump_version, evaluate_agent_candidate

def review(task, evidence, safety, fmt, reproducibility):
    return {"scores":{"task_success":task,"evidence_and_factuality":evidence,"safety_and_permissions":safety,
      "format_and_completeness":fmt,"reproducibility":reproducibility},"hard_fail_flags":[],"pass_threshold":70,"reviewer_id":"unit-test"}

class AgentEvolutionTests(unittest.TestCase):
    def test_semver_bumps(self):
        self.assertEqual(bump_version("0.1.0","patch"),"0.1.1")
        self.assertEqual(bump_version("0.1.0","minor"),"0.2.0")
        self.assertEqual(bump_version("0.1.0","major"),"1.0.0")
    def test_improvement_waits_for_human(self):
        r=evaluate_agent_candidate(agent_id="social_content_creator",current_version="0.1.0",candidate_version="0.1.1",
          baseline_review=review(70,70,90,70,70),candidate_review=review(90,85,90,90,85),
          regression_results={"unit":True,"format":True},change_type="patch")
        self.assertEqual(r["status"],"candidate_passed_awaiting_human_approval"); self.assertFalse(r["promoted"])
        self.assertGreater(r["score_delta"],0)
    def test_approved_still_requires_manual_promotion(self):
        r=evaluate_agent_candidate(agent_id="app_builder_coder",current_version="0.1.0",candidate_version="0.2.0",
          baseline_review=review(60,70,90,70,70),candidate_review=review(95,90,90,90,90),
          regression_results={"unit":True},change_type="minor",human_approved=True)
        self.assertEqual(r["status"],"approved_for_manual_promotion"); self.assertFalse(r["promoted"])
    def test_regression_failure_blocks(self):
        r=evaluate_agent_candidate(agent_id="video_reel_writer",current_version="0.1.0",candidate_version="0.1.1",
          baseline_review=review(70,70,90,70,70),candidate_review=review(95,90,90,90,90),
          regression_results={"unit":True,"safety":False},change_type="patch")
        self.assertEqual(r["status"],"rejected_regression_failure")
    def test_safety_drop_blocks(self):
        r=evaluate_agent_candidate(agent_id="data_extractor",current_version="0.1.0",candidate_version="0.1.1",
          baseline_review=review(70,70,90,70,70),candidate_review=review(99,99,89,99,99),
          regression_results={"unit":True},change_type="patch")
        self.assertEqual(r["status"],"rejected_safety_score_drop")
    def test_wrong_candidate_version_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_agent_candidate(agent_id="test",current_version="0.1.0",candidate_version="0.1.4",
              baseline_review=review(70,70,90,70,70),candidate_review=review(90,90,90,90,90),
              regression_results={"unit":True},change_type="patch")

if __name__ == "__main__": unittest.main()
