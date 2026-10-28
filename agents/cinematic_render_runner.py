"""Run a selected cinematic-ad concept through an approved ComfyUI API workflow.

The renderer is only invoked with explicit execution approval. This runner never
publishes content or claims a job finished unless output files are retrieved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agents.comfyui_render_client import (
    ComfyUIClient,
    ComfyUIError,
    validate_api_workflow,
)


def prepare_concept(pack: dict[str, Any], concept_id: str) -> dict[str, Any]:
    if not isinstance(pack, dict) or not isinstance(pack.get("concepts"), list):
        raise ComfyUIError("Creative pack must contain a concepts list")
    gate = pack.get("quality_gate", {})
    if gate.get("status") != "DRAFT_REVIEW_REQUIRED":
        raise ComfyUIError("Creative pack is not ready for review; quality gate is not passed")
    matches = [item for item in pack["concepts"] if isinstance(item, dict) and item.get("concept_id") == concept_id]
    if len(matches) != 1:
        raise ComfyUIError(f"Expected exactly one concept named {concept_id}")
    shots = matches[0].get("shots")
    if not isinstance(shots, list) or not shots:
        raise ComfyUIError("Selected concept has no shot list")
    for shot in shots:
        if not isinstance(shot, dict) or not all(
            isinstance(shot.get(key), str) and shot[key].strip()
            for key in ("time", "scene_direction", "visual_prompt", "motion_prompt")
        ):
            raise ComfyUIError("Every shot must include time, direction, visual prompt and motion prompt")
    return matches[0]


def run_concept(
    pack_path: str | Path,
    workflow_path: str | Path,
    concept_id: str,
    *,
    execute: bool = False,
    wait: bool = False,
    image_path: str | Path | None = None,
    asset_permission_confirmed: bool = False,
    output_dir: str | Path = "artifacts/comfyui",
    timeout_seconds: int = 900,
    seed: int | None = None,
    negative_prompt: str = "flicker, morphing, deformed products, distorted logos, gibberish text, inconsistent identity",
    client: ComfyUIClient | None = None,
) -> dict[str, Any]:
    if not execute:
        raise ComfyUIError("Rendering requires explicit approval via execute=True or CLI --execute")
    if image_path and not asset_permission_confirmed:
        raise ComfyUIError("Confirm permission to use the input image via --asset-permission-confirmed")
    try:
        pack = json.loads(Path(pack_path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ComfyUIError(f"Cannot read creative pack: {type(exc).__name__}") from None
    except json.JSONDecodeError:
        raise ComfyUIError("Creative pack is not valid JSON") from None
    try:
        workflow = json.loads(Path(workflow_path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ComfyUIError(f"Cannot read workflow: {type(exc).__name__}") from None
    except json.JSONDecodeError:
        raise ComfyUIError("ComfyUI workflow is not valid JSON") from None
    workflow = validate_api_workflow(workflow)
    workflow_text = json.dumps(workflow)
    if "__AUTOPILOT_POSITIVE_PROMPT__" not in workflow_text:
        raise ComfyUIError("Workflow must include __AUTOPILOT_POSITIVE_PROMPT__ so each shot prompt is applied")
    needs_image = "__AUTOPILOT_IMAGE_FILENAME__" in workflow_text
    if needs_image and not image_path:
        raise ComfyUIError("This workflow requires an input image; supply --image and confirm permissions")
    if image_path and not needs_image:
        raise ComfyUIError("An image was supplied but the workflow has no image placeholder")
    concept = prepare_concept(pack, concept_id)
    client = client or ComfyUIClient()
    report: dict[str, Any] = {
        "schema_version": "cinematic_render_run_v1",
        "client": pack.get("client", {}),
        "pack_id": pack.get("pack_id"),
        "concept_id": concept_id,
        "concept_title": concept.get("title"),
        "status": "RUNNING",
        "shot_results": [],
        "execution_truth": {
            "explicit_execution_approval": True,
            "research_performed": bool(pack.get("execution_truth", {}).get("research_performed", False)),
            "llm_inference_used_for_concept_pack": bool(pack.get("execution_truth", {}).get("llm_inference_used", False)),
            "render_jobs_submitted": False,
            "output_files_downloaded": False,
            "published": False,
        },
    }
    failures = 0
    for index, shot in enumerate(concept["shots"], start=1):
        full_prompt = (
            f"Commercial shot {shot['time']} for {report['client'].get('business_type', 'business')}. "
            f"{shot['scene_direction']} Visual direction: {shot['visual_prompt']} "
            f"Motion direction: {shot['motion_prompt']} Preserve the supplied real product, person, "
            "logo and brand details; add no image text because typography is added in editing."
        )
        prefix = f"autopilot_{concept_id}_{index:02d}".replace("-", "_")
        entry: dict[str, Any] = {"shot_index": index, "time": shot["time"], "status": "NOT_SUBMITTED"}
        try:
            submission = client.submit_workflow(
                workflow_path, approved=True, image_path=image_path,
                positive_prompt=full_prompt, negative_prompt=negative_prompt,
                seed=(seed + index - 1) if seed is not None else None,
                output_prefix=prefix,
            )
            entry["prompt_id"] = submission["prompt_id"]
            entry["status"] = "SUBMITTED"
            report["execution_truth"]["render_jobs_submitted"] = True
            if wait:
                finished = client.wait_for_outputs(submission["prompt_id"], Path(output_dir) / prefix,
                                                   timeout_seconds=timeout_seconds)
                entry["status"] = finished["status"].upper()
                entry["outputs"] = finished.get("outputs", [])
                if finished.get("output_downloaded"):
                    report["execution_truth"]["output_files_downloaded"] = True
            else:
                entry["output_downloaded"] = False
        except (ComfyUIError, OSError, ValueError) as exc:
            failures += 1
            entry["status"] = "FAILED"
            entry["error_type"] = type(exc).__name__
            entry["error"] = str(exc)
        report["shot_results"].append(entry)
    statuses = [item["status"] for item in report["shot_results"]]
    if failures:
        report["status"] = "PARTIAL_OR_FAILED"
    elif wait and all(status == "COMPLETED" for status in statuses):
        report["status"] = "COMPLETED_WITH_OUTPUTS"
    else:
        report["status"] = "SUBMITTED_PENDING_OUTPUTS"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True, help="JSON from agents.cinematic_ad_planner")
    parser.add_argument("--workflow", required=True, help="ComfyUI API-format workflow JSON with prompt placeholder")
    parser.add_argument("--concept", default="route_1")
    parser.add_argument("--image", help="Optional client/reference image; only sent to the configured ComfyUI endpoint")
    parser.add_argument("--asset-permission-confirmed", action="store_true")
    parser.add_argument("--execute", action="store_true", help="Explicitly approve generation of selected shot jobs")
    parser.add_argument("--wait", action="store_true", help="Wait for shot outputs and download files")
    parser.add_argument("--output-dir", default="artifacts/cinematic-renders")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    try:
        report = run_concept(args.pack, args.workflow, args.concept, execute=args.execute,
            wait=args.wait, image_path=args.image,
            asset_permission_confirmed=args.asset_permission_confirmed,
            output_dir=args.output_dir, timeout_seconds=args.timeout_seconds, seed=args.seed)
        output_path = Path(args.output_dir) / "render-run-report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "concept": report["concept_title"],
            "shots": len(report["shot_results"]), "jobs_submitted": report["execution_truth"]["render_jobs_submitted"],
            "files_downloaded": report["execution_truth"]["output_files_downloaded"],
            "report": str(output_path)}, ensure_ascii=False))
        return 0 if report["status"] in {"COMPLETED_WITH_OUTPUTS", "SUBMITTED_PENDING_OUTPUTS"} else 1
    except (ComfyUIError, OSError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
