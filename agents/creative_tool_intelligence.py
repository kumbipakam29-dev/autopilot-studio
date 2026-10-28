"""Creative tool intelligence registry and evidence-led improvement loop.

This module turns public, citable observations into original experiments and
compares candidate outputs with a transparent rubric. It does not clone private
code, bypass access controls, or assert performance without measured evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

REGISTRY_VERSION = "creative_tool_intelligence_v1"

# Treat this as a research starter catalog, not an endorsement or fixed price list.
# License/cost status should be rechecked before each commercial deployment.
TOOL_CATALOG: list[dict[str, Any]] = [
    {
        "id": "comfyui",
        "name": "ComfyUI",
        "category": ["workflow_orchestration", "image", "video", "audio", "3d", "editing"],
        "access": "open_source_local_core",
        "cost_model": "no mandatory local-core subscription; hardware, models and custom nodes vary",
        "useful_public_behaviour": ["node graph workflows", "reusable subgraphs", "local API", "workflow JSON", "offload and quantized model support"],
        "autopilot_adaptation": "Build a pluggable workflow runner with input/output contracts and saved, versioned graphs.",
        "cautions": ["custom-node licenses vary", "inspect graphs for paid/provider nodes", "local hardware and model requirements vary"],
        "sources": [
            "https://github.com/Comfy-Org/ComfyUI",
            "https://github.com/Comfy-Org/docs/blob/main/development/api-development/workflow-api-format.mdx",
        ],
    },
    {
        "id": "wan22",
        "name": "Wan2.2",
        "category": ["text_to_video", "image_to_video", "video"],
        "access": "open_weights_local",
        "cost_model": "no per-generation API fee when run locally; hardware and setup required",
        "useful_public_behaviour": ["video generation from text or images", "published inference code and weights"],
        "autopilot_adaptation": "Offer as a local image-to-video candidate after device, version and license checks.",
        "cautions": ["confirm exact checkpoint and dependency requirements", "test actual VRAM/runtime before promising speed or quality"],
        "sources": ["https://github.com/Wan-Video/Wan2.2"],
    },
    {
        "id": "ltx25",
        "name": "LTX-2.5",
        "category": ["text_to_video", "image_to_video", "audio_video"],
        "access": "open_weights_community_license",
        "cost_model": "local inference may avoid per-call API fees; hardware and license terms apply",
        "useful_public_behaviour": ["video generation ecosystem", "audio/video workflow"],
        "autopilot_adaptation": "Evaluate as an optional local workflow candidate, gated on exact release license and commercial eligibility.",
        "cautions": ["not treat as unrestricted Apache/MIT", "read current license for the exact version before commercial use"],
        "sources": ["https://github.com/Lightricks/LTX-2", "https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x"],
    },
    {
        "id": "vbench",
        "name": "VBench",
        "category": ["video_evaluation", "benchmark"],
        "access": "open_source_evaluation_code",
        "cost_model": "code is public; running evaluations may require compute and dependencies",
        "useful_public_behaviour": ["separates video quality into dimensions", "includes subject/background consistency, flicker, motion smoothness, aesthetic and imaging quality"],
        "autopilot_adaptation": "Borrow the evaluation dimensions as inspiration; build a lightweight first-pass QA rubric and add VBench later if hardware allows.",
        "cautions": ["a score is not customer-sales proof", "check dataset/code/model terms before use"],
        "sources": ["https://github.com/Vchitect/VBench"],
    },
    {
        "id": "ideogram",
        "name": "Ideogram",
        "category": ["image_generation", "poster_typography", "image_editing"],
        "access": "hosted_service",
        "cost_model": "free/paid entitlements and API terms may change",
        "useful_public_behaviour": ["designed for text-heavy image composition", "editable text layer workflows"],
        "autopilot_adaptation": "Use as an optional comparison reference for poster typography; keep final business text editable and proofread.",
        "cautions": ["vendor accuracy numbers are claims, not independent guarantees", "verify plan, commercial use and data retention"],
        "sources": ["https://ideogram.ai/features/text-rendering/", "https://docs.ideogram.ai/"],
    },
    {
        "id": "pika",
        "name": "Pika",
        "category": ["image_to_video", "keyframe_animation", "effects"],
        "access": "hosted_service",
        "cost_model": "credit-based; limits, watermark and pricing depend on plan/model",
        "useful_public_behaviour": ["animate a still", "transition between ordered keyframes", "prompt-guided motion"],
        "autopilot_adaptation": "Implement an original keyframe-bridging stage; compare our locally rendered transitions against references.",
        "cautions": ["credits and watermark affect cost", "review current terms and consent rights for uploaded faces"],
        "sources": ["https://creation.pika.art/apps/pikaframes?tab=video-tools", "https://pika.art/faq"],
    },
    {
        "id": "krea",
        "name": "Krea",
        "category": ["image_generation", "video_generation", "upscale", "editing", "realtime"],
        "access": "hosted_multi_model_service",
        "cost_model": "free access and paid limits vary; confirm current usage terms",
        "useful_public_behaviour": ["multi-model image/video access", "editing and enhancement", "style/product tuning"],
        "autopilot_adaptation": "Study the separation between generation, edit, enhancement and reusable brand/style references.",
        "cautions": ["hosted model access is not the same as local/open weights", "check rights and privacy for client uploads"],
        "sources": ["https://www.krea.ai/"],
    },
    {
        "id": "canva_magic_video",
        "name": "Canva Magic Video / Magic Studio",
        "category": ["social_design", "video_assembly", "template_adaptation"],
        "access": "hosted_freemium",
        "cost_model": "feature availability varies by plan, account and locale",
        "useful_public_behaviour": ["turn clips/photos into template-guided edits with transitions and music", "editable design workflow"],
        "autopilot_adaptation": "Create editable layout/export templates only after our concept and story have passed originality checks.",
        "cautions": ["template-first output can look generic", "verify AI-feature access and commercial asset licenses"],
        "sources": ["https://www.canva.com/help/magic-video/"],
    },
    {
        "id": "adobe_firefly_agent",
        "name": "Adobe Firefly Creative Agent",
        "category": ["brand_system", "storyboard", "product_video", "quick_cut"],
        "access": "proprietary_hosted",
        "cost_model": "plan/credit limits apply; verify current terms",
        "useful_public_behaviour": ["brand kit generation", "storyboards to video", "product-photo video", "automated first cut"],
        "autopilot_adaptation": "Implement the same broad stage separation independently: brand context, storyboard, shot generation and editorial assembly.",
        "cautions": ["do not claim access to private Adobe internals", "licensed asset and model terms must be checked"],
        "sources": ["https://news.adobe.com/news/2026/06/adobe-unveils-major-expansion"],
    },
    {
        "id": "runway_workflows",
        "name": "Runway Workflows / Ads",
        "category": ["model_routing", "product_video", "workflow_automation", "ad_creative"],
        "access": "proprietary_hosted",
        "cost_model": "credit-based/API billing; not assumed free",
        "useful_public_behaviour": ["chain multiple generation/editing steps", "reusable workflows", "route models by cost, quality and latency"],
        "autopilot_adaptation": "Create our own transparent model-router interface with measured latency/cost/quality and fallback rules.",
        "cautions": ["no hidden paid fallback in AutoPilot", "connectors require an explicit budget/permission check"],
        "sources": ["https://dev.runwayml.com/workflows", "https://dev.runwayml.com/learn/generate-product-videos"],
    },
    {
        "id": "ffmpeg",
        "name": "FFmpeg",
        "category": ["video_editing", "transcode", "audio_mix", "export"],
        "access": "open_source_local",
        "cost_model": "no per-render API fee; binary and build license depend on configuration",
        "useful_public_behaviour": ["video/audio filters", "transcoding", "format and bitrate control", "stream mapping"],
        "autopilot_adaptation": "Use for deterministic assembly, crop/scale, audio mix and platform export after AI shots arrive.",
        "cautions": ["inspect build/licensing when redistributing", "validate codec, aspect ratio, safe area and output size"],
        "sources": ["https://www.ffmpeg.org/ffmpeg.html", "https://www.ffmpeg.org/documentation.html"],
    },
]

TASK_TOOL_MAP = {
    "premium_cinematic_reel": ["comfyui", "wan22", "ltx25", "pika", "krea", "runway_workflows", "ffmpeg", "vbench"],
    "image_to_video": ["comfyui", "wan22", "ltx25", "pika", "krea", "runway_workflows"],
    "text_heavy_poster": ["ideogram", "canva_magic_video", "comfyui", "adobe_firefly_agent"],
    "storyboard": ["comfyui", "adobe_firefly_agent", "runway_workflows", "krea"],
    "video_quality_review": ["vbench", "ffmpeg", "comfyui"],
    "brand_consistency": ["comfyui", "krea", "adobe_firefly_agent", "runway_workflows"],
    "video_edit_export": ["ffmpeg", "canva_magic_video", "runway_workflows"],
}

METRIC_WEIGHTS = {
    "brief_fit": 0.18,
    "concept_diversity": 0.14,
    "product_identity_fidelity": 0.18,
    "temporal_consistency": 0.15,
    "factuality": 0.18,
    "visual_legibility": 0.10,
    "technical_export": 0.07,
}
HARD_GATES = (
    "asset_rights_confirmed",
    "commercial_license_cleared",
    "no_unsupported_claims",
    "no_direct_imitation",
    "privacy_review_passed",
    "actual_outputs_exist",
)


def list_tools() -> list[dict[str, Any]]:
    return [dict(tool) for tool in TOOL_CATALOG]


def recommend_tools(task: str, *, zero_budget: bool = True, local_only: bool = True) -> dict[str, Any]:
    requested = task.strip().lower()
    if requested not in TASK_TOOL_MAP:
        raise ValueError("Unsupported task. Choose: " + ", ".join(sorted(TASK_TOOL_MAP)))
    lookup = {tool["id"]: tool for tool in TOOL_CATALOG}
    candidates = []
    for tool_id in TASK_TOOL_MAP[requested]:
        tool = lookup[tool_id]
        reasons = []
        penalty = 0
        if zero_budget:
            if tool["access"] in {"open_source_local", "open_source_local_core", "open_weights_local", "open_source_evaluation_code"}:
                reasons.append("local/public-code candidate; still check model and dependency terms")
            elif tool["access"] == "open_weights_community_license":
                reasons.append("local candidate, but license check is a hard commercial gate")
                penalty += 2
            else:
                reasons.append("hosted proprietary/free-tier availability must be verified")
                penalty += 4
        if local_only and ("hosted" in tool["access"] or "proprietary" in tool["access"]):
            reasons.append("does not meet strict local-only preference")
            penalty += 5
        candidates.append({
            "tool_id": tool_id,
            "name": tool["name"],
            "access": tool["access"],
            "cost_model": tool["cost_model"],
            "reasons": reasons,
            "preference_penalty": penalty,
            "autopilot_adaptation": tool["autopilot_adaptation"],
            "sources": tool["sources"],
        })
    candidates.sort(key=lambda item: (item["preference_penalty"], item["tool_id"]))
    return {
        "task": requested,
        "policy": {"zero_budget_preferred": zero_budget, "local_only_preferred": local_only,
                   "no_silent_paid_fallback": True},
        "recommendations": candidates,
        "disclaimer": "Rank is a policy-based shortlist, not a quality benchmark. Validate current license, hardware, access and actual output.",
    }


def _validate_metrics(metrics: dict[str, Any], field: str) -> dict[str, float]:
    if not isinstance(metrics, dict):
        raise ValueError(f"{field} must be an object of metric scores from 0 to 5")
    out = {}
    for metric in METRIC_WEIGHTS:
        value = metrics.get(metric)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 5:
            raise ValueError(f"{field}.{metric} must be a numeric value from 0 to 5")
        out[metric] = float(value)
    return out


def _validate_observation(observation: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(observation, dict):
        raise TypeError("observation must be a JSON object")
    required = ("tool_name", "source_url", "observed_on", "public_behavior", "input_output_observed", "unknowns")
    normalized = dict(observation)
    for key in required:
        value = normalized.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"observation.{key} must be a non-empty string")
    if not re.match(r"^https://", normalized["source_url"]):
        raise ValueError("source_url must be an HTTPS URL to public evidence")
    try:
        date.fromisoformat(normalized["observed_on"])
    except ValueError:
        raise ValueError("observed_on must use YYYY-MM-DD") from None
    normalized["evidence_scope"] = normalized.get("evidence_scope", "public_demo_or_documentation")
    if normalized["evidence_scope"] not in {"public_demo_or_documentation", "authorized_test_output", "public_research_paper"}:
        raise ValueError("evidence_scope must reference public or authorized evidence only")
    normalized["private_code_accessed"] = False
    normalized["access_controls_bypassed"] = False
    return normalized


def _weighted_score(metrics: dict[str, float]) -> float:
    return round(sum(metrics[name] * weight for name, weight in METRIC_WEIGHTS.items()) / 5 * 100, 2)


def build_reverse_engineering_cycle(raw: dict[str, Any]) -> dict[str, Any]:
    """Compare an original candidate with a measured baseline from public/authorized evidence."""
    if not isinstance(raw, dict):
        raise TypeError("cycle input must be an object")
    observation = _validate_observation(raw.get("observation"))
    experiment_name = raw.get("experiment_name")
    if not isinstance(experiment_name, str) or not experiment_name.strip():
        raise ValueError("experiment_name must be a non-empty string")
    baseline = _validate_metrics(raw.get("baseline_metrics"), "baseline_metrics")
    candidate = _validate_metrics(raw.get("candidate_metrics"), "candidate_metrics")
    gates = raw.get("hard_gates")
    if not isinstance(gates, dict) or any(not isinstance(gates.get(key), bool) for key in HARD_GATES):
        raise ValueError("hard_gates must provide boolean values for: " + ", ".join(HARD_GATES))
    change_log = raw.get("original_changes")
    if not isinstance(change_log, list) or not change_log or any(not isinstance(item, str) or not item.strip() for item in change_log):
        raise ValueError("original_changes must be a non-empty list of original implementation changes")
    baseline_score = _weighted_score(baseline)
    candidate_score = _weighted_score(candidate)
    delta = round(candidate_score - baseline_score, 2)
    gates_passed = all(gates[key] is True for key in HARD_GATES)
    if gates_passed and delta > 0:
        decision = "PROMOTE_CANDIDATE_TO_HUMAN_REVIEW"
    elif not gates_passed:
        decision = "BLOCK_PROMOTION_FIX_HARD_GATES"
    else:
        decision = "KEEP_BASELINE_OR_RUN_ANOTHER_EXPERIMENT"
    serial = json.dumps({
        "experiment_name": experiment_name,
        "observation": observation,
        "baseline_metrics": baseline,
        "candidate_metrics": candidate,
        "hard_gates": gates,
        "original_changes": change_log,
    }, ensure_ascii=False, sort_keys=True)
    return {
        "schema_version": REGISTRY_VERSION,
        "cycle_id": hashlib.sha256(serial.encode("utf-8")).hexdigest()[:16],
        "experiment_name": experiment_name,
        "observed_tool": observation,
        "reverse_engineering_scope": "public_behavioral_analysis_and_original_reimplementation",
        "original_changes": change_log,
        "benchmark": {
            "metric_scale": "0-5; must be assessed from actual outputs by rubric or evaluator",
            "weights": METRIC_WEIGHTS,
            "baseline_metrics": baseline,
            "candidate_metrics": candidate,
            "baseline_score": baseline_score,
            "candidate_score": candidate_score,
            "delta": delta,
            "scores_are_measured_inputs": True,
            "independent_quality_or_sales_claim": False,
        },
        "hard_gates": gates,
        "hard_gates_passed": gates_passed,
        "decision": decision,
        "next_loop": (
            "Have a human compare output files, approve/reject the candidate, record issues, and run the same benchmark again."
            if decision == "PROMOTE_CANDIDATE_TO_HUMAN_REVIEW"
            else "Record failed metrics, change one or two implementation variables, then rerun the same benchmark."
        ),
        "safety_truth": {
            "private_code_copied": False,
            "access_controls_bypassed": False,
            "production_auto_deployed": False,
            "paid_provider_auto_selected": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-tools", action="store_true")
    parser.add_argument("--task", help="Task for a tool shortlist")
    parser.add_argument("--allow-hosted", action="store_true", help="Do not prefer local-only tools")
    parser.add_argument("--allow-paid-options", action="store_true", help="Do not prioritize zero-budget tools")
    parser.add_argument("--cycle", help="Path to a JSON evidence/benchmark cycle input")
    parser.add_argument("--output", default="artifacts/creative-tool-intelligence.json")
    args = parser.parse_args()
    try:
        if args.list_tools:
            result: Any = {"registry_version": REGISTRY_VERSION, "tools": list_tools()}
        elif args.task:
            result = recommend_tools(args.task, zero_budget=not args.allow_paid_options, local_only=not args.allow_hosted)
        elif args.cycle:
            result = build_reverse_engineering_cycle(json.loads(Path(args.cycle).read_text(encoding="utf-8")))
        else:
            parser.error("use --list-tools, --task, or --cycle")
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "REPORT_CREATED", "output": str(path),
                          "registry_version": REGISTRY_VERSION}, ensure_ascii=False))
        return 0
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
