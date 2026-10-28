import json
import unittest
from unittest.mock import patch

from agents.cinematic_ad_planner import build_cinematic_ad_pack


class CinematicAdPlannerTests(unittest.TestCase):
    def brief(self, business_type="salon"):
        return {
            "client_name": "Demo Client",
            "business_type": business_type,
            "audience": "local customers",
            "goal": "increase qualified enquiries",
            "offer_or_topic": "hair styling services",
            "brand_voice": "confident and warm",
            "call_to_action": "Book a consultation",
            "work_types": ["reel_video"],
            "platforms": ["instagram"],
            "approved_facts": ["Consultations available by appointment"],
            "prohibited_claims": [],
            "brand_colors": ["black", "rose gold"],
            "reference_notes": ["Use the customer's real salon photos"],
            "client_asset_permission_confirmed": False,
            "publish_approval": False,
        }

    def test_creates_three_distinct_routes_with_timed_shots(self):
        pack = build_cinematic_ad_pack(self.brief())
        self.assertEqual(len(pack["concepts"]), 3)
        self.assertEqual(len({x["title"] for x in pack["concepts"]}), 3)
        self.assertTrue(all(len(x["shots"]) == 4 for x in pack["concepts"]))
        self.assertEqual(pack["quality_gate"]["status"], "DRAFT_REVIEW_REQUIRED")
        self.assertEqual(pack["generation_mode"], "deterministic_industry_routes")

    def test_routes_are_business_specific(self):
        salon = build_cinematic_ad_pack(self.brief("salon"))
        auto = build_cinematic_ad_pack(self.brief("auto parts store"))
        self.assertIn("Mirror reveal", [x["title"] for x in salon["concepts"]])
        self.assertIn("Precision exploded view", [x["title"] for x in auto["concepts"]])

    def test_optional_llm_routes_are_validated_and_attributed(self):
        routes = [
            {"title": "Material close-up", "story": "Start with a real service detail.",
             "visual_mechanic": "macro_push", "motion_direction": "Slow forward camera move.",
             "payoff": "Every detail matters."},
            {"title": "Tools choreography", "story": "Choreograph approved tools around the service.",
             "visual_mechanic": "tool_orbit", "motion_direction": "Precise low-speed orbit.",
             "payoff": "Craft in motion."},
            {"title": "Mirror moment", "story": "End with a consent-approved final look.",
             "visual_mechanic": "mirror_match_cut", "motion_direction": "Soft match cut.",
             "payoff": "Your moment, your style."},
        ]
        with patch("agents.llm_router.chat_completion", return_value={
            "content": json.dumps(routes), "model": "qwen3:4b", "provider_mode": "local_endpoint"
        }) as mocked:
            pack = build_cinematic_ad_pack(self.brief(), use_llm=True)
        mocked.assert_called_once()
        self.assertEqual(pack["generation_mode"], "configured_llm")
        self.assertEqual(pack["llm"]["model"], "qwen3:4b")
        self.assertTrue(pack["execution_truth"]["llm_inference_used"])
        self.assertFalse(pack["execution_truth"]["video_rendered"])

    def test_llm_malformed_response_fails_closed(self):
        with patch("agents.llm_router.chat_completion", return_value={
            "content": "not-json", "model": "qwen3:4b", "provider_mode": "local_endpoint"
        }):
            with self.assertRaises(ValueError):
                build_cinematic_ad_pack(self.brief(), use_llm=True)

    def test_routes_cover_multiple_business_categories(self):
        cases = [
            ("fitness studio", "Movement in one beat"),
            ("real estate agency", "Doorway-to-view"),
            ("education center", "Concept comes alive"),
            ("ecommerce store", "Material-to-use"),
            ("software company", "Problem-to-workflow"),
            ("music artist", "Studio-to-stage"),
            ("healthcare clinic", "Care environment"),
            ("travel hospitality", "Arrival reveal"),
            ("fashion boutique", "Fabric in motion"),
            ("jewellery shop", "Light on the detail"),
            ("construction contractor", "Blueprint-to-build"),
            ("general retail store", "Aisle-to-hero"),
        ]
        for business_type, expected_title in cases:
            with self.subTest(business_type=business_type):
                pack = build_cinematic_ad_pack(self.brief(business_type))
                self.assertIn(expected_title, [item["title"] for item in pack["concepts"]])

    def test_pack_does_not_claim_media_rendered_or_published(self):
        pack = build_cinematic_ad_pack(self.brief())
        self.assertFalse(pack["execution_truth"]["image_rendered"])
        self.assertFalse(pack["execution_truth"]["video_rendered"])
        self.assertFalse(pack["execution_truth"]["published"])
        self.assertFalse(pack["quality_gate"]["rendered_assets_verified"])

    def test_invalid_brief_is_rejected(self):
        with self.assertRaises(ValueError):
            build_cinematic_ad_pack({"client_name": "Missing fields"})


if __name__ == "__main__":
    unittest.main()
