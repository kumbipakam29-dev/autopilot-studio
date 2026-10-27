"""Regression tests for the offline client-acquisition draft pipeline."""
import unittest

from agents.client_acquisition_pipeline import build_client_acquisition_pack


class ClientAcquisitionPipelineTests(unittest.TestCase):
    def test_returns_complete_draft_pack_without_external_side_effects(self):
        result = build_client_acquisition_pack({
            "business_name": "Demo Cafe",
            "business_type": "cafe",
            "location": "Ahmedabad",
            "audience": "nearby office workers",
            "offer": "breakfast and coffee",
            "platforms": ["Instagram", "Facebook"],
            "call_to_action": "Ask us about today's menu",
            "facts": ["The owner supplied this example fact"],
            "specific_public_fact": "your supplied public menu mentions breakfast",
        })
        self.assertEqual(result["status"], "draft_pack_ready_for_human_review")
        self.assertEqual(len(result["caption_drafts"]["drafts"]), 3)
        self.assertEqual(len(result["seven_day_calendar"]["calendar"]), 7)
        self.assertEqual(len(result["reel_scripts"]), 2)
        self.assertTrue(all(item["duration_sec"] == 17 for item in result["reel_scripts"]))
        self.assertIn("FICTIONAL SPEC WORK", result["portfolio_spec_work"]["label"])
        self.assertFalse(result["safety"]["outreach_sent"])
        self.assertFalse(result["safety"]["content_published"])
        self.assertFalse(result["safety"]["live_prospect_research_performed"])
        self.assertTrue(result["safety"]["human_review_required"])
        self.assertEqual(result["outreach_draft"]["status"], "draft_for_human_review")

    def test_does_not_invent_personalization_when_no_fact_supplied(self):
        result = build_client_acquisition_pack({
            "business_type": "salon",
            "audience": "local residents",
            "offer": "hair services",
            "platforms": ["Instagram"],
        })
        self.assertIsNone(result["outreach_draft"]["draft"])
        self.assertEqual(result["outreach_draft"]["status"], "needs_specific_fact")
        self.assertIn("specific_public_fact_for_outreach", result["missing_inputs"])

    def test_marks_missing_brief_fields_and_only_uses_supplied_facts(self):
        result = build_client_acquisition_pack({"business_type": "repair shop"})
        self.assertIn("audience", result["missing_inputs"])
        self.assertIn("offer", result["missing_inputs"])
        self.assertTrue(result["safety"]["uses_user_supplied_facts_only"])
        self.assertFalse(result["safety"]["external_sources_fetched"])

    def test_rejects_non_dictionary_input(self):
        with self.assertRaises(TypeError):
            build_client_acquisition_pack("not a brief")


if __name__ == "__main__":
    unittest.main()
