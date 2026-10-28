import unittest

from agents.creative_tool_intelligence import (
    HARD_GATES,
    TOOL_CATALOG,
    analyze_public_observation,
    append_cycle_ledger,
    build_reverse_engineering_cycle,
    next_experiment,
    recommend_tools,
    summarize_cycle_ledger,
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
        "metrics_are_actual": True,
        "metric_provenance": "Test-controlled scores for unit-testing decision logic; not claims about real media quality.",
        "hard_gates": {key: gates for key in HARD_GATES},
        "original_changes": [
            "Use a client-specific storyboard with separate shot prompts.",
            "Keep exact logo and CTA editable in post rather than baking text into generated pixels.",
        ],
    }


class CreativeToolIntelligenceTests(unittest.TestCase):
    def test_registry_has_sources_and_cautions(self):
        self.assertGreaterEqual(len(TOOL_CATALOG), 13)
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

    def test_public_observation_creates_original_hypotheses(self):
        observation = cycle_input()["observation"]
        report = analyze_public_observation(observation)
        titles = [item["title"] for item in report["original_hypotheses"]]
        self.assertIn("Reference-image anchoring", titles)
        self.assertFalse(report["safety_truth"]["private_code_copied"])
        self.assertTrue(all(item["basis"] == "publicly observable behavior only"
                            for item in report["original_hypotheses"]))

    def test_typography_observation_suggests_editable_text_layers(self):
        observation = cycle_input()["observation"]
        observation["public_behavior"] = "The public tool demonstrates text rendering for a promotional poster."
        report = analyze_public_observation(observation)
        self.assertIn("Editable typography pass", [item["title"] for item in report["original_hypotheses"]])

    def test_all_catalog_task_maps_reference_known_tools(self):
        from agents.creative_tool_intelligence import TASK_TOOL_MAP
        known = {item["id"] for item in TOOL_CATALOG}
        for task, tools in TASK_TOOL_MAP.items():
            with self.subTest(task=task):
                self.assertTrue(tools)
                self.assertTrue(set(tools).issubset(known))

    def test_repository_public_observations_generate_hypotheses(self):
        import json
        from pathlib import Path
        observations = sorted(Path("examples").glob("creative-tool-observation-*.json"))
        self.assertGreaterEqual(len(observations), 4)
        for path in observations:
            with self.subTest(path=path.name):
                report = analyze_public_observation(json.loads(path.read_text(encoding="utf-8")))
                self.assertTrue(report["original_hypotheses"])
                self.assertFalse(report["safety_truth"]["private_code_copied"])

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

    def test_placeholder_measurements_never_promote(self):
        data = cycle_input()
        data["metrics_are_actual"] = False
        data["metric_provenance"] = "Template values only; no media exists yet."
        report = build_reverse_engineering_cycle(data)
        self.assertEqual(report["decision"], "NEED_REAL_OUTPUT_MEASUREMENTS")
        self.assertFalse(report["benchmark"]["scores_are_measured_inputs"])

    def test_ledger_appends_once_and_summarizes_measured_results(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.jsonl"
            report = build_reverse_engineering_cycle(cycle_input())
            first = append_cycle_ledger(path, report)
            second = append_cycle_ledger(path, report)
            summary = summarize_cycle_ledger(path)
        self.assertTrue(first["inserted"])
        self.assertFalse(second["inserted"])
        self.assertEqual(summary["cycle_count"], 1)
        self.assertEqual(summary["measured_cycle_count"], 1)
        self.assertIsNotNone(summary["best_measured_candidate"])

    def test_ledger_excludes_placeholder_metrics_from_best_candidate(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.jsonl"
            data = cycle_input()
            data["metrics_are_actual"] = False
            report = build_reverse_engineering_cycle(data)
            append_cycle_ledger(path, report)
            summary = summarize_cycle_ledger(path)
        self.assertEqual(summary["measured_cycle_count"], 0)
        self.assertIsNone(summary["best_measured_candidate"])

    def test_next_experiment_targets_weakest_measured_dimension(self):
        result = next_experiment(metrics(4), metrics_are_actual=True)
        self.assertIn(result["target_dimension"], metrics(4))
        self.assertTrue(result["experiment"])
        unmeasured = next_experiment(metrics(0), metrics_are_actual=False)
        self.assertEqual(unmeasured["target_dimension"], "unmeasured")

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

    def test_private_code_or_access_bypass_is_rejected(self):
        data = cycle_input()
        data["observation"]["private_code_accessed"] = True
        with self.assertRaises(ValueError):
            build_reverse_engineering_cycle(data)

    def test_unknown_or_private_scope_is_rejected(self):
        data = cycle_input()
        data["observation"]["evidence_scope"] = "private_code_access"
        with self.assertRaises(ValueError):
            build_reverse_engineering_cycle(data)


if __name__ == "__main__":
    unittest.main()
