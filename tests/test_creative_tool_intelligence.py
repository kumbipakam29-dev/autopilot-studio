import unittest

from agents.creative_tool_intelligence import (
    HARD_GATES,
    TOOL_CATALOG,
    build_reverse_engineering_cycle,
    recommend_tools,
)


def metrics(value):
    return {
        "brief_fit": value,
        "concept_diversity": value,
        "product_identity_fidelity": value,
        "temporal_consistency": value,
        "factuality": value,
        "visual_legibility": value,
        "technical_export": value,
    }


def cycle_input(baseline=3, candidate=4, gates=True):
    return {
        "experiment_name": "photo-to-cinematic-ad-loop-v1",
        "observation": {
            "tool_name": "Public demo tool",
            "source_url": "https://example.com/public-demo",
            "observed_on": "2026-10-28",
            "public_behavior": "An uploaded product photo is used as a visual anchor for a short animation.",
            "input_output_observed": "One still image produces a short moving clip with preserved framing.",
            "unknowns": "Underlying model, internal prompts and exact production stack are not verified.",
            "evidence_scope": "public_demo_or_documentation",
        },
        "baseline_metrics": metrics(baseline),
        "candidate_metrics": metrics(candidate),
        "hard_gates": {key: gates for key in HARD_GATES},
        "original_changes": [
            "Use a client-specific storyboard with separate shot prompts.",
            "Keep exact logo and CTA editable in post rather than baking text into generated pixels.",
        ],
    }


class CreativeToolIntelligenceTests(unittest.TestCase):
    def test_registry_has_sources_and_cautions(self):
        self.assertGreaterEqual(len(TOOL_CATALOG), 10)
        for tool in TOOL_CATALOG:
            self.assertTrue(tool["sources"])
            self.assertTrue(tool["cautions"])
            self.assertTrue(tool["autopilot_adaptation"])

    def test_local_zero_budget_video_shortlist_prefers_local_candidates(self):
        result = recommend_tools("premium_cinematic_reel", zero_budget=True, local_only=True)
        self.assertTrue(result["policy"]["no_silent_paid_fallback"])
        self.assertEqual(result["recommendations"][0]["tool_id"], "comfyui")
        self.assertTrue(any(item["tool_id"] == "wan22" for item in result["recommendations"]))

    def test_unsupported_task_rejected(self):
        with self.assertRaises(ValueError):
            recommend_tools("mind_reading")

    def test_cycle_promotes_only_when_score_improves_and_all_gates_pass(self):
        report = build_reverse_engineering_cycle(cycle_input())
        self.assertGreater(report["benchmark"]["candidate_score"], report["benchmark"]["baseline_score"])
        self.assertEqual(report["decision"], "PROMOTE_CANDIDATE_TO_HUMAN_REVIEW")
        self.assertFalse(report["safety_truth"]["private_code_copied"])
        self.assertFalse(report["safety_truth"]["production_auto_deployed"])

    def test_cycle_blocks_hard_gate_failure_even_if_score_improves(self):
        data = cycle_input()
        data["hard_gates"]["commercial_license_cleared"] = False
        report = build_reverse_engineering_cycle(data)
        self.assertEqual(report["decision"], "BLOCK_PROMOTION_FIX_HARD_GATES")

    def test_cycle_keeps_baseline_when_candidate_not_better(self):
        report = build_reverse_engineering_cycle(cycle_input(baseline=4, candidate=4))
        self.assertEqual(report["decision"], "KEEP_BASELINE_OR_RUN_ANOTHER_EXPERIMENT")

    def test_observation_requires_https_public_evidence(self):
        data = cycle_input()
        data["observation"]["source_url"] = "file:///private/repo"
        with self.assertRaises(ValueError):
            build_reverse_engineering_cycle(data)

    def test_metric_scale_is_strict(self):
        data = cycle_input()
        data["candidate_metrics"]["factuality"] = 7
        with self.assertRaises(ValueError):
            build_reverse_engineering_cycle(data)

    def test_unknown_or_private_scope_is_rejected(self):
        data = cycle_input()
        data["observation"]["evidence_scope"] = "private_code_access"
        with self.assertRaises(ValueError):
            build_reverse_engineering_cycle(data)


if __name__ == "__main__":
    unittest.main()
