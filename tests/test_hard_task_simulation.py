import unittest
from agents.hard_task_simulation import COMPUTE_TASKS, CREATIVE_BRIEF, build_content_pack, run_hard_task_suite, simulate_virtual_ram_schedule

class HardTaskSimulationTests(unittest.TestCase):
    def test_compute_budget_never_exceeded(self):
        result = simulate_virtual_ram_schedule(COMPUTE_TASKS, budget_mb=512, max_parallel=2)
        self.assertLessEqual(result["peak_virtual_ram_mb"], 512)
        self.assertTrue(result["never_oversubscribed"])
        self.assertFalse(result["real_os_ram_allocated"])

    def test_oversized_job_blocked(self):
        result = simulate_virtual_ram_schedule(COMPUTE_TASKS, budget_mb=512)
        self.assertIn("oversized-model-probe", result["blocked_task_ids"])

    def test_transient_failure_retried(self):
        result = simulate_virtual_ram_schedule(COMPUTE_TASKS)
        self.assertTrue(result["transient_failure_recovered"])
        item = next(x for x in result["outcomes"] if x["task_id"] == "injected-transient-failure")
        self.assertEqual(item["attempts"], 2)

    def test_duplicate_ids_rejected(self):
        task = {"task_id":"x","memory_mb":1,"duration_ticks":1}
        with self.assertRaises(ValueError):
            simulate_virtual_ram_schedule([task, task])

    def test_offer_must_be_approved(self):
        brief = dict(CREATIVE_BRIEF)
        brief["approved_facts"] = []
        with self.assertRaises(ValueError):
            build_content_pack(brief)

    def test_creative_pack_passes_format_checks_and_is_draft(self):
        result = build_content_pack(CREATIVE_BRIEF)
        self.assertTrue(all(result["checks"].values()), result["checks"])
        self.assertEqual(len(result["caption_drafts"]), 3)
        self.assertEqual(len(result["seven_day_calendar"]), 7)
        self.assertFalse(result["published"])
        self.assertTrue(result["draft_only"])

    def test_report_never_allows_customer_delivery(self):
        report = run_hard_task_suite()
        self.assertFalse(report["execution_truth"]["live_llm_called"])
        self.assertFalse(report["quality_gate"]["customer_delivery_allowed"])
        self.assertEqual(report["learning_cycle"]["task_id"], "hard-task-suite-v1")

if __name__ == "__main__":
    unittest.main()
