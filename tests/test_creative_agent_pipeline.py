import unittest

from agents.creative_agent_pipeline import build_agent_pipeline


class CreativeAgentPipelineTests(unittest.TestCase):
    def brief(self, business_type="salon"):
        return {
            "client_name": "Demo Client",
            "business_type": business_type,
            "audience": "local customers",
            "goal": "increase qualified enquiries",
            "offer_or_topic": "hair styling services",
            "brand_voice": "confident and warm",
            "call_to_action": "Book a consultation",
            "work_types": ["reel_video", "social_content"],
            "platforms": ["instagram"],
            "approved_facts": ["Consultations available by appointment"],
            "prohibited_claims": [],
            "brand_colors": ["black", "rose gold"],
            "reference_notes": ["Premium cinematic motion"],
            "client_asset_permission_confirmed": False,
            "publish_approval": False,
        }

    def test_creates_auditable_agent_handoffs(self):
        result = build_agent_pipeline(self.brief())
        names = [task["agent"] for task in result["agent_tasks"]]
        self.assertIn("creative_director_agent", names)
        self.assertIn("motion_agent", names)
        self.assertIn("quality_agent", names)
        self.assertIn("publishing_agent", names)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(result["cinematic_ad_pack"]["concepts"]), 3)
        self.assertTrue(result["execution_truth"]["rule_based_creative_plan_generated"])
        self.assertEqual(result["tool_intelligence"]["registry_version"], "creative_tool_intelligence_v1")
        self.assertFalse(result["tool_intelligence"]["live_tool_discovery_performed"])
        self.assertTrue(result["tool_intelligence"]["recommendations"])
        self.assertTrue(all(item["policy"]["no_silent_paid_fallback"] for item in result["tool_intelligence"]["recommendations"]))

    def test_does_not_claim_render_or_publish(self):
        result = build_agent_pipeline(self.brief())
        self.assertFalse(result["execution_truth"]["video_rendered"])
        self.assertFalse(result["execution_truth"]["published"])
        self.assertTrue(any("renderer" in task["status"].lower() for task in result["agent_tasks"]))
        self.assertEqual(next(t for t in result["agent_tasks"] if t["agent"] == "research_agent")["status"],
                         "BLOCKED_NO_RESEARCH_CONNECTOR")

    def test_business_type_is_carried_into_work_order(self):
        result = build_agent_pipeline(self.brief("auto parts store"))
        self.assertEqual(result["client"]["business_type"], "auto parts store")
        self.assertIn("Precision exploded view",
                      [x["title"] for x in result["cinematic_ad_pack"]["concepts"]])

    def test_invalid_brief_is_rejected(self):
        with self.assertRaises(ValueError):
            build_agent_pipeline({"client_name": "Missing fields"})


if __name__ == "__main__":
    unittest.main()
