import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "runtime" / "runner.py"
SPEC = importlib.util.spec_from_file_location("aps_runner", MODULE)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)

class RunnerTests(unittest.TestCase):
    def test_routes_content_task_without_external_action(self):
        result = runner.run_task({"task_type": "draft_content", "input": {"topic": "cafe"}})
        self.assertEqual(result["status"], "review_required")
        self.assertFalse(result["approval_required"])
        self.assertEqual(result["agent_id"], "content-planner")

    def test_payment_record_requires_approval(self):
        result = runner.run_task({"task_type": "record_payment", "input": {"amount": 0}})
        self.assertEqual(result["status"], "awaiting_user_approval")
        self.assertTrue(result["approval_required"])

    def test_unknown_task_type_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "No registered agent"):
            runner.run_task({"task_type": "execute_shell", "input": {}})

    def test_missing_fields_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Missing required fields"):
            runner.run_task({"task_type": "draft_content"})

    def test_rejects_unexpected_fields(self):
        with self.assertRaisesRegex(ValueError, "Unexpected fields"):
            runner.run_task({"task_type": "draft_content", "input": {}, "shell": "whoami"})

    def test_input_must_be_object(self):
        with self.assertRaisesRegex(ValueError, "input must be an object"):
            runner.run_task({"task_type": "draft_content", "input": "not-an-object"})

    def test_rejects_non_object_task(self):
        with self.assertRaisesRegex(ValueError, "Task must be a JSON object"):
            runner.run_task([])

if __name__ == "__main__":
    unittest.main()
