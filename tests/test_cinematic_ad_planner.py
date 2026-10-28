import unittest

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

    def test_routes_are_business_specific(self):
        salon = build_cinematic_ad_pack(self.brief("salon"))
        auto = build_cinematic_ad_pack(self.brief("auto parts store"))
        self.assertIn("Mirror reveal", [x["title"] for x in salon["concepts"]])
        self.assertIn("Precision exploded view", [x["title"] for x in auto["concepts"]])

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
