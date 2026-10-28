import json
import tempfile
import unittest
from pathlib import Path

from agents.comfyui_render_client import ComfyUIError
from agents.cinematic_render_runner import prepare_concept, run_concept


def sample_pack():
    shots = []
    for index, time in enumerate(("0-2s", "2-6s", "6-13s", "13-18s"), start=1):
        shots.append({
            "time": time,
            "scene_direction": f"Scene {index}",
            "visual_prompt": f"Visual prompt {index}",
            "motion_prompt": f"Motion prompt {index}",
        })
    return {
        "pack_id": "pack123",
        "client": {"name": "Demo", "business_type": "salon"},
        "quality_gate": {"status": "DRAFT_REVIEW_REQUIRED"},
        "execution_truth": {"research_performed": False, "llm_inference_used": False},
        "concepts": [{"concept_id": "route_1", "title": "Mirror reveal", "shots": shots}],
    }


class FakeClient:
    def __init__(self):
        self.submissions = []
        self.finished = []

    def submit_workflow(self, workflow_path, **kwargs):
        self.submissions.append(kwargs)
        return {"prompt_id": f"job_{len(self.submissions)}"}

    def wait_for_outputs(self, prompt_id, output_dir, **kwargs):
        self.finished.append(prompt_id)
        return {"status": "completed", "outputs": [str(Path(output_dir) / "clip.mp4")],
                "output_downloaded": True}


class CinematicRenderRunnerTests(unittest.TestCase):
    def write_json(self, path, data):
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_prepare_concept_requires_passed_quality_gate(self):
        pack = sample_pack()
        self.assertEqual(prepare_concept(pack, "route_1")["title"], "Mirror reveal")
        pack["quality_gate"]["status"] = "HOLD_FOR_REVIEW"
        with self.assertRaises(ComfyUIError):
            prepare_concept(pack, "route_1")

    def test_execute_approval_is_required(self):
        with self.assertRaises(ComfyUIError):
            run_concept("missing-pack.json", "missing-workflow.json", "route_1", execute=False)

    def test_client_image_requires_permission_confirmation(self):
        with self.assertRaises(ComfyUIError):
            run_concept("missing-pack.json", "missing-workflow.json", "route_1",
                        execute=True, image_path="client-photo.png", asset_permission_confirmed=False)

    def test_queues_four_shots_and_waits_for_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pack_path = self.write_json(root / "pack.json", sample_pack())
            workflow_path = self.write_json(root / "workflow.json", {
                "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "__AUTOPILOT_POSITIVE_PROMPT__"}}
            })
            fake = FakeClient()
            report = run_concept(pack_path, workflow_path, "route_1", execute=True, wait=True,
                                 output_dir=root / "rendered", client=fake)
        self.assertEqual(len(fake.submissions), 4)
        self.assertEqual(len(fake.finished), 4)
        self.assertEqual(report["status"], "COMPLETED_WITH_OUTPUTS")
        self.assertTrue(report["execution_truth"]["render_jobs_submitted"])
        self.assertTrue(report["execution_truth"]["output_files_downloaded"])
        self.assertFalse(report["execution_truth"]["published"])
        self.assertTrue(all("Visual prompt" in item["positive_prompt"] for item in fake.submissions))

    def test_rejects_workflow_without_positive_prompt_placeholder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pack_path = self.write_json(root / "pack.json", sample_pack())
            workflow_path = self.write_json(root / "workflow.json", {
                "1": {"class_type": "EmptyNode", "inputs": {}}
            })
            with self.assertRaises(ComfyUIError):
                run_concept(pack_path, workflow_path, "route_1", execute=True, client=FakeClient())


if __name__ == "__main__":
    unittest.main()
