"""Guarded client for an explicitly approved local ComfyUI workflow.

This adapter submits a user-reviewed API-format workflow to ComfyUI, substitutes
AutoPilot placeholder values, and optionally downloads completed output files.
It does not build/install models or guarantee that a workflow is free of all
third-party providers; review workflows before execution.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "http://127.0.0.1:8188"
DEFAULT_TIMEOUT_SECONDS = 30
OUTPUT_GROUPS = ("images", "gifs", "videos", "audio", "files")
REMOTE_PROVIDER_TOKENS = (
    "replicate", "falai", "openai", "kling", "luma", "runpod",
    "stabilityai", "googleveo", "pika", "cloudapi",
)


class ComfyUIError(RuntimeError):
    """ComfyUI is unavailable or the requested workflow cannot be run safely."""


@dataclass(frozen=True)
class ComfyUIConfig:
    base_url: str
    timeout_seconds: int
    bearer_token: str | None
    remote: bool
    allow_remote_nodes: bool


def load_config(environ: dict[str, str] | None = None) -> ComfyUIConfig:
    env = os.environ if environ is None else environ
    base = env.get("AUTOPILOT_COMFYUI_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
    if not base.startswith(("http://", "https://")):
        raise ComfyUIError("ComfyUI base URL must use HTTP(S)")
    parsed = urlsplit(base)
    if not parsed.netloc or parsed.username or parsed.password:
        raise ComfyUIError("ComfyUI URL must be a valid host URL without embedded credentials")
    remote = parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
    if remote and env.get("AUTOPILOT_ALLOW_REMOTE_COMFYUI", "").lower() != "true":
        raise ComfyUIError(
            "Remote ComfyUI is disabled. Use a trusted private endpoint and set "
            "AUTOPILOT_ALLOW_REMOTE_COMFYUI=true only after reviewing its security."
        )
    try:
        timeout = int(env.get("AUTOPILOT_COMFYUI_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    except ValueError:
        raise ComfyUIError("AUTOPILOT_COMFYUI_TIMEOUT_SECONDS must be an integer") from None
    if not 1 <= timeout <= 180:
        raise ComfyUIError("ComfyUI request timeout must be between 1 and 180 seconds")
    return ComfyUIConfig(
        base_url=base,
        timeout_seconds=timeout,
        bearer_token=env.get("AUTOPILOT_COMFYUI_BEARER_TOKEN", "").strip() or None,
        remote=remote,
        allow_remote_nodes=env.get("AUTOPILOT_COMFYUI_ALLOW_PROVIDER_NODES", "").lower() == "true",
    )


def validate_api_workflow(workflow: Any) -> dict[str, Any]:
    if not isinstance(workflow, dict) or not workflow:
        raise ComfyUIError("Workflow must be a non-empty ComfyUI API-format node dictionary")
    for node_id, node in workflow.items():
        if not isinstance(node, dict) or not isinstance(node.get("class_type"), str):
            raise ComfyUIError(
                "Workflow must use ComfyUI API-format nodes with class_type and inputs; "
                "export the workflow in API format, not normal UI format."
            )
        if not isinstance(node.get("inputs"), dict):
            raise ComfyUIError(f"Node {node_id} must contain an inputs object")
    return workflow


def find_potential_remote_nodes(workflow: dict[str, Any]) -> list[str]:
    names = []
    for node in workflow.values():
        class_type = node.get("class_type", "")
        low = class_type.lower()
        if any(token in low for token in REMOTE_PROVIDER_TOKENS):
            names.append(class_type)
    return sorted(set(names))


def substitute_placeholders(
    workflow: dict[str, Any],
    *,
    positive_prompt: str | None = None,
    negative_prompt: str | None = None,
    image_filename: str | None = None,
    seed: int | None = None,
    output_prefix: str = "autopilot",
) -> dict[str, Any]:
    tokens: dict[str, Any] = {
        "__AUTOPILOT_POSITIVE_PROMPT__": positive_prompt,
        "__AUTOPILOT_NEGATIVE_PROMPT__": negative_prompt,
        "__AUTOPILOT_IMAGE_FILENAME__": image_filename,
        "__AUTOPILOT_SEED__": seed,
        "__AUTOPILOT_OUTPUT_PREFIX__": output_prefix,
    }

    def replace_value(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: replace_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace_value(item) for item in value]
        if isinstance(value, str):
            for token, replacement in tokens.items():
                if value == token:
                    if replacement is None:
                        raise ComfyUIError(f"Workflow needs {token}, but no matching value was supplied")
                    return replacement
            result = value
            for token, replacement in tokens.items():
                if token in result:
                    if replacement is None:
                        raise ComfyUIError(f"Workflow needs {token}, but no matching value was supplied")
                    result = result.replace(token, str(replacement))
            if "__AUTOPILOT_" in result:
                raise ComfyUIError("Workflow contains an unknown AutoPilot placeholder")
            return result
        return value

    return replace_value(workflow)


class ComfyUIClient:
    def __init__(self, config: ComfyUIConfig | None = None):
        self.config = config or load_config()

    def _request(self, path: str, *, data: bytes | None = None,
                 content_type: str | None = None, method: str | None = None) -> bytes:
        headers: dict[str, str] = {}
        if content_type:
            headers["Content-Type"] = content_type
        if self.config.bearer_token:
            headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        request = Request(self.config.base_url + path, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                return response.read()
        except HTTPError as exc:
            raise ComfyUIError(f"ComfyUI returned HTTP {exc.code}") from None
        except (URLError, TimeoutError, OSError) as exc:
            raise ComfyUIError(f"ComfyUI unavailable: {type(exc).__name__}") from None

    def _get_json(self, path: str) -> dict[str, Any]:
        try:
            result = json.loads(self._request(path).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ComfyUIError("ComfyUI returned invalid JSON") from None
        if not isinstance(result, dict):
            raise ComfyUIError("ComfyUI returned an unexpected JSON structure")
        return result

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        encoded = json.dumps(payload).encode("utf-8")
        try:
            result = json.loads(self._request(path, data=encoded,
                content_type="application/json", method="POST").decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ComfyUIError("ComfyUI returned invalid JSON") from None
        if not isinstance(result, dict):
            raise ComfyUIError("ComfyUI returned an unexpected JSON structure")
        return result

    def check_server(self) -> dict[str, Any]:
        stats = self._get_json("/system_stats")
        devices = stats.get("devices", [])
        return {
            "status": "connected",
            "base_url": self.config.base_url,
            "remote_endpoint": self.config.remote,
            "device_count": len(devices) if isinstance(devices, list) else 0,
            "model_rendering_tested": False,
            "note": "Server health checked only; no generation job was submitted.",
        }

    def upload_image(self, image_path: str | Path) -> str:
        path = Path(image_path)
        if not path.is_file():
            raise ComfyUIError("Input image file does not exist")
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
            raise ComfyUIError("Unsupported input image extension")
        if path.stat().st_size > 40 * 1024 * 1024:
            raise ComfyUIError("Input image exceeds the 40 MiB safety limit")
        boundary = uuid.uuid4().hex
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        image_bytes = path.read_bytes()
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="{path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8") + image_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
        try:
            result = json.loads(self._request("/upload/image", data=body,
                content_type=f"multipart/form-data; boundary={boundary}", method="POST").decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ComfyUIError("ComfyUI image upload returned invalid JSON") from None
        if not isinstance(result, dict) or not isinstance(result.get("name"), str):
            raise ComfyUIError("ComfyUI image upload did not return an image name")
        subfolder = result.get("subfolder", "")
        if subfolder and (".." in Path(subfolder).parts or Path(subfolder).is_absolute()):
            raise ComfyUIError("ComfyUI returned an unsafe image subfolder")
        return f"{subfolder}/{result['name']}" if subfolder else result["name"]

    def submit_workflow(
        self,
        workflow_path: str | Path,
        *,
        approved: bool = False,
        image_path: str | Path | None = None,
        positive_prompt: str | None = None,
        negative_prompt: str | None = None,
        seed: int | None = None,
        output_prefix: str = "autopilot",
    ) -> dict[str, Any]:
        if not approved:
            raise ComfyUIError("Execution requires explicit approval via approved=True or CLI --execute")
        try:
            workflow = json.loads(Path(workflow_path).read_text(encoding="utf-8"))
        except OSError as exc:
            raise ComfyUIError(f"Cannot read workflow file: {type(exc).__name__}") from None
        except json.JSONDecodeError:
            raise ComfyUIError("Workflow file is not valid JSON") from None
        workflow = validate_api_workflow(workflow)
        external_nodes = find_potential_remote_nodes(workflow)
        if external_nodes and not self.config.allow_remote_nodes:
            raise ComfyUIError(
                "Workflow contains possible remote/provider nodes ("
                + ", ".join(external_nodes)
                + "). Review for data transfer and billing before setting "
                "AUTOPILOT_COMFYUI_ALLOW_PROVIDER_NODES=true."
            )
        serialized = json.dumps(workflow)
        needs_image = "__AUTOPILOT_IMAGE_FILENAME__" in serialized
        if needs_image and not image_path:
            raise ComfyUIError("Workflow requires an input image placeholder but --image was not supplied")
        if image_path and not needs_image:
            raise ComfyUIError("An input image was supplied but the workflow has no image placeholder")
        workflow = substitute_placeholders(
            workflow, positive_prompt=positive_prompt, negative_prompt=negative_prompt,
            image_filename="__AUTOPILOT_IMAGE_PENDING_UPLOAD__" if needs_image else None,
            seed=seed, output_prefix=output_prefix,
        )
        image_filename = self.upload_image(image_path) if needs_image and image_path else None

        def replace_uploaded_name(value: Any) -> Any:
            if isinstance(value, dict):
                return {key: replace_uploaded_name(item) for key, item in value.items()}
            if isinstance(value, list):
                return [replace_uploaded_name(item) for item in value]
            if isinstance(value, str):
                return value.replace("__AUTOPILOT_IMAGE_PENDING_UPLOAD__", image_filename or "")
            return value

        workflow = replace_uploaded_name(workflow)
        response = self._post_json("/prompt", {"prompt": workflow})
        prompt_id = response.get("prompt_id")
        if not isinstance(prompt_id, str) or not prompt_id:
            errors = response.get("node_errors")
            raise ComfyUIError("ComfyUI did not return a prompt_id; node_errors_present="
                               + str(bool(errors)))
        return {
            "status": "submitted",
            "prompt_id": prompt_id,
            "workflow_node_errors": response.get("node_errors", {}),
            "provider_nodes_found": external_nodes,
            "output_downloaded": False,
        }

    def wait_for_outputs(self, prompt_id: str, output_dir: str | Path, *,
                         timeout_seconds: int = 900, poll_interval_seconds: float = 2.0) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", prompt_id):
            raise ComfyUIError("Invalid prompt_id")
        if timeout_seconds < 1 or timeout_seconds > 3600:
            raise ComfyUIError("Output wait timeout must be between 1 and 3600 seconds")
        if poll_interval_seconds < 0.1 or poll_interval_seconds > 30:
            raise ComfyUIError("Poll interval must be between 0.1 and 30 seconds")
        deadline = time.monotonic() + timeout_seconds
        entry = None
        while time.monotonic() < deadline:
            history = self._get_json("/history/" + prompt_id)
            entry = history.get(prompt_id, history if "outputs" in history else None)
            if isinstance(entry, dict):
                status = entry.get("status", {})
                status_text = status.get("status_str", "") if isinstance(status, dict) else ""
                if status_text.lower() in {"error", "failed"}:
                    raise ComfyUIError("ComfyUI reported job failure; inspect ComfyUI logs")
                if isinstance(entry.get("outputs"), dict):
                    output_items = self._collect_outputs(entry["outputs"])
                    if output_items:
                        break
            time.sleep(poll_interval_seconds)
        else:
            raise ComfyUIError(f"Timed out waiting for ComfyUI job {prompt_id}")
        folder = Path(output_dir)
        folder.mkdir(parents=True, exist_ok=True)
        saved = []
        for index, item in enumerate(output_items, start=1):
            filename = item.get("filename")
            if not isinstance(filename, str) or Path(filename).name != filename:
                raise ComfyUIError("ComfyUI returned an unsafe output filename")
            subfolder = item.get("subfolder", "")
            if not isinstance(subfolder, str) or Path(subfolder).is_absolute() or ".." in Path(subfolder).parts:
                raise ComfyUIError("ComfyUI returned an unsafe output subfolder")
            kind = item.get("type", "output")
            query = urlencode({"filename": filename, "subfolder": subfolder, "type": kind})
            data = self._request("/view?" + query)
            safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(filename).stem)[:80] or "output"
            suffix = Path(filename).suffix[:12]
            target = folder / f"{prompt_id[:8]}_{index:02d}_{safe_stem}{suffix}"
            target.write_bytes(data)
            saved.append(str(target))
        return {
            "status": "completed",
            "prompt_id": prompt_id,
            "outputs": saved,
            "output_downloaded": bool(saved),
            "workflow_completed_with_outputs": bool(saved),
        }

    @staticmethod
    def _collect_outputs(outputs: dict[str, Any]) -> list[dict[str, Any]]:
        collected = []
        for node_result in outputs.values():
            if not isinstance(node_result, dict):
                continue
            for key in OUTPUT_GROUPS:
                items = node_result.get(key, [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and isinstance(item.get("filename"), str):
                            collected.append(item)
        return collected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check ComfyUI server health only")
    parser.add_argument("--workflow", help="Path to exported ComfyUI API-format workflow JSON")
    parser.add_argument("--image", help="Optional input image for image-to-video workflows")
    parser.add_argument("--positive-prompt")
    parser.add_argument("--negative-prompt")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--output-prefix", default="autopilot")
    parser.add_argument("--execute", action="store_true", help="Explicitly approve workflow execution")
    parser.add_argument("--wait", action="store_true", help="Wait for outputs and download them")
    parser.add_argument("--output-dir", default="artifacts/comfyui")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    args = parser.parse_args()
    try:
        client = ComfyUIClient()
        if args.check:
            print(json.dumps(client.check_server(), ensure_ascii=False, indent=2))
            return 0
        if not args.workflow:
            parser.error("--workflow is required unless --check is used")
        result = client.submit_workflow(args.workflow, approved=args.execute, image_path=args.image,
            positive_prompt=args.positive_prompt, negative_prompt=args.negative_prompt,
            seed=args.seed, output_prefix=args.output_prefix)
        if args.wait:
            result = client.wait_for_outputs(result["prompt_id"], args.output_dir,
                                             timeout_seconds=args.timeout_seconds)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ComfyUIError, OSError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
