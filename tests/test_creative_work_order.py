import unittest
from agents.creative_work_order import build_creative_work_order, validate_client_brief

BASE = {
    "client_name": "Bluebird Cafe", "business_type": "cafe",
    "audience": "students and remote workers", "goal": "increase weekday visits",
    "offer_or_topic": "quiet coffee break with a pastry", "brand_voice": "friendly and thoughtful",
    "call_to_action": "Ask about today's menu", "platforms": ["instagram", "facebook"],
    "work_types": ["social_content", "reel_video", "poster_design", "social_media_management"],
    "approved_facts": ["quiet coffee break with a pastry"],
    "prohibited_claims": ["cheapest in town"], "brand_colors": ["navy", "cream"],
}

class CreativeWorkOrderTests(unittest.TestCase):
    def test_multiple_distinct_client_specific_deliverables(self):
        result = build_creative_work_order(BASE)
        self.assertEqual(set(result["deliverables"]), set(BASE["work_types"]))
        self.assertEqual(result["quality_gate"]["status"], "DRAFT_REVIEW_REQUIRED")
        self.assertFalse(result["quality_gate"]["customer_delivery_allowed"])
        self.assertIn("students and remote workers", str(result["deliverables"]))
        self.assertEqual(result["deliverables"]["reel_video"]["duration_seconds"], 18)
        self.assertEqual(len(result["deliverables"]["social_media_management"]["weekly_mix"]), 7)
        self.assertFalse(result["execution_truth"]["social_posts_published"])

    def test_business_type_changes_creative_route(self):
        cafe = build_creative_work_order(BASE)
        salon_brief = dict(BASE, client_name="Studio Glow", business_type="salon")
        salon = build_creative_work_order(salon_brief)
        self.assertNotEqual(cafe["deliverables"]["social_content"]["concepts"][0]["visual"],
                            salon["deliverables"]["social_content"]["concepts"][0]["visual"])

    def test_unknown_task_rejected(self):
        with self.assertRaises(ValueError):
            validate_client_brief(dict(BASE, work_types=["magic_everything"]))

    def test_required_brief_field_rejected(self):
        brief = dict(BASE)
        brief.pop("audience")
        with self.assertRaises(ValueError):
            build_creative_work_order(brief)

    def test_prohibited_claim_trips_quality_gate(self):
        brief = dict(BASE, prohibited_claims=["a closer look at quiet coffee break with a pastry"])
        result = build_creative_work_order(brief)
        self.assertEqual(result["quality_gate"]["status"], "HOLD_FOR_HUMAN_REVIEW")
        self.assertFalse(result["quality_gate"]["customer_delivery_allowed"])

    def test_website_and_billing_have_security_gates(self):
        brief = dict(BASE, work_types=["website_build", "billing_system"])
        result = build_creative_work_order(brief)
        self.assertIn("keyboard navigation", str(result["deliverables"]["website_build"]))
        self.assertIn("No real charges", result["deliverables"]["billing_system"]["release_gate"])

    def test_music_uses_rights_gate_and_does_not_claim_rendering(self):
        result = build_creative_work_order(dict(BASE, work_types=["music_concept"]))
        self.assertIn("usage rights", result["deliverables"]["music_concept"]["rights_gate"])
        self.assertFalse(result["execution_truth"]["music_rendered"])

if __name__ == "__main__":
    unittest.main()
