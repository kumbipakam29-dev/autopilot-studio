import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.comfyui_render_client import (
    DEFAULT_BASE_URL,
    ComfyUIClient,
    ComfyUIConfig,
    ComfyUIError,
    find_potential_remote_nodes,
    load_config,
    substitute_placeholders,
    validate_api_workflow,
)


class ComfyUIRenderClientTests(unittest.TestCase):
    def config(self, *, allow_remote_nodes=False):
        return ComfyUIConfig(DEFAULT_BASE_URL, 2, None, False, allow_remote_nodes)

    def workflow(self):
        return {
            "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "__AUTOPILOT_POSITIVE_PROMPT__"}},
            "2": {"class_type": "LoadImage", "inputs": {"image": "__AUTOPILOT_IMAGE_FILENAME__"}},
            "3": {"class_type": "KSampler", "inputs": {"seed": "__AUTOPILOT_SEED__"}},
            "4": {"class_type": "SaveVideo", "inputs": {"filename_prefix": "__AUTOPILOT_OUTPUT_PREFIX__"}},
        }

    def test_default_config_is_local(self):
        cfg = load_config({})
        self.assertEqual(cfg.base_url, DEFAULT_BASE_URL)
        self.assertFalse(cfg.remote)

    def test_remote_endpoint_requires_explicit_opt_in(self):
        with self.assertRaises(ComfyUIError):
            load_config({"AUTOPILOT_COMFYUI_BASE_URL": "https://render.example"})
        cfg = load_config({
            "AUTOPILOT_COMFYUI_BASE_URL": "https://render.example",
            "AUTOPILOT_ALLOW_REMOTE_COMFYUI": "true",
        })
        self.assertTrue(cfg.remote)

    def test_api_workflow_must_be_exported_node_dictionary(self):
        with self.assertRaises(ComfyUIError):
            validate_api_workflow({"nodes": [], "links": []})

    def test_placeholder_replacement_keeps_seed_as_integer(self):
        result = substitute_placeholders(self.workflow(), positive_prompt="cinematic macro",
            image_filename="input.png", seed=123, output_prefix="client_ad")
        self.assertEqual(result["1"]["inputs"]["text"], "cinematic macro")
        self.assertEqual(result["2"]["inputs"]["image"], "input.png")
        self.assertEqual(result["3"]["inputs"]["seed"], 123)
        self.assertEqual(result["4"]["inputs"]["filename_prefix"], "client_ad")

    def test_missing_placeholder_value_is_rejected(self):
        with self.assertRaises(ComfyUIError):
            substitute_placeholders(self.workflow(), positive_prompt="test")

    def test_obvious_remote_provider_nodes_are_detected(self):
        workflow = {"1": {"class_type": "KlingImageToVideo", "inputs": {}}}
        self.assertEqual(find_potential_remote_nodes(workflow), ["KlingImageToVideo"])
        with self.assertRaises(ComfyUIError):
            validate_api_workflow({"1": {"inputs": {}}})

    def test_execution_requires_explicit_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "workflow.json"
            path.write_text(json.dumps(self.workflow()), encoding="utf-8")
            client = ComfyUIClient(self.config())
            with self.assertRaises(ComfyUIError):
                client.submit_workflow(path, approved=False)

    def test_submit_uses_placeholders_and_reports_job_id(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "workflow.json"
            path.write_text(json.dumps(self.workflow()), encoding="utf-8")
            client = ComfyUIClient(self.config())
            with patch.object(client, "upload_image", return_value="uploaded.png"), \
                 patch.object(client, "_post_json", return_value={"prompt_id": "job_123", "node_errors": {}}) as post:
                result = client.submit_workflow(path, approved=True, image_path="source.jpg",
                    positive_prompt="branded cinematic product", seed=42)
            submitted = post.call_args.args[1]["prompt"]
            self.assertEqual(result["prompt_id"], "job_123")
            self.assertEqual(submitted["2"]["inputs"]["image"], "uploaded.png")
            self.assertEqual(submitted["3"]["inputs"]["seed"], 42)
            self.assertFalse(result["output_downloaded"])

    def test_unsafe_output_prefix_rejected_before_file_access(self):
        client = ComfyUIClient(self.config())
        with self.assertRaises(ComfyUIError):
            client.submit_workflow("does-not-exist.json", approved=True, output_prefix="../outside")

    def test_unused_input_image_is_not_uploaded(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "workflow.json"
            workflow = {"1": {"class_type": "KSampler", "inputs": {"seed": 42}}}
            path.write_text(json.dumps(workflow), encoding="utf-8")
            client = ComfyUIClient(self.config())
            with patch.object(client, "upload_image") as upload:
                with self.assertRaises(ComfyUIError):
                    client.submit_workflow(path, approved=True, image_path="source.jpg")
            upload.assert_not_called()

    def test_provider_nodes_blocked_by_default(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "workflow.json"
            path.write_text(json.dumps({"1": {"class_type": "KlingImageToVideo", "inputs": {}}}), encoding="utf-8")
            client = ComfyUIClient(self.config())
            with self.assertRaises(ComfyUIError):
                client.submit_workflow(path, approved=True)

    def test_wait_downloads_completed_output(self):
        with tempfile.TemporaryDirectory() as temp:
            client = ComfyUIClient(self.config())
            history = {"job_123": {"outputs": {"8": {"gifs": [
                {"filename": "clip.mp4", "subfolder": "", "type": "output"}
            ]}}}}
            with patch.object(client, "_get_json", return_value=history), \
                 patch.object(client, "_request", return_value=b"fake-video-bytes"):
                result = client.wait_for_outputs("job_123", temp, timeout_seconds=2)
            self.assertEqual(result["status"], "completed")
            self.assertTrue(Path(result["outputs"][0]).is_file())
            self.assertTrue(result["workflow_completed_with_outputs"])


if __name__ == "__main__":
    unittest.main()
