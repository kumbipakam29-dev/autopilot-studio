"""Auditable, client-specific handoffs for cinematic ad production.

The pipeline prepares a concrete production pack and exposes blocked integrations
honestly. It does not call external research tools, render media, publish or spend.
"""
import argparse
import hashlib
import json
from pathlib import Path

from agents.creative_work_order import build_creative_work_order
from agents.cinematic_ad_planner import build_cinematic_ad_pack

AGENTS = [
    ("intake_agent", "Validate brief, approved facts and asset permissions", []),
    ("research_agent", "Find cited public competitor patterns; do not copy", ["intake_agent"]),
    ("creative_director_agent", "Develop distinct client-specific campaign concepts", ["intake_agent"]),
    ("script_agent", "Write hook, shot list, on-screen copy and CTA", ["creative_director_agent"]),
    ("visual_agent", "Specify framing, lighting, product fidelity and brand style", ["creative_director_agent"]),
    ("motion_agent", "Animate approved stills with controlled camera and subject motion", ["visual_agent"]),
    ("sound_agent", "Plan sound design and verify music rights", ["script_agent"]),
    ("editor_agent", "Assemble shots, pacing, captions and platform exports", ["script_agent", "motion_agent", "sound_agent"]),
    ("quality_agent", "Check factuality, originality, legibility, fidelity and technical quality", ["editor_agent", "visual_agent"]),
    ("approval_agent", "Package previews and collect explicit client approval", ["quality_agent"]),
    ("publishing_agent", "Publish only after approval through authorized integrations", ["approval_agent"]),
]

def build_agent_pipeline(brief, *, use_llm=False):
    order = build_creative_work_order(brief)
    brief_ok = order["quality_gate"]["status"] == "DRAFT_REVIEW_REQUIRED"
    work_types = set(brief.get("work_types", []))
    wants_video = bool(work_types.intersection({"reel_video", "video_ad"}))
    cinematic_pack = build_cinematic_ad_pack(brief, use_llm=use_llm) if wants_video and brief_ok else None

    statuses = {
        "intake_agent": "BRIEF_VALIDATED" if brief_ok else "BLOCKED_BRIEF_QUALITY_GATE",
        "research_agent": "BLOCKED_NO_RESEARCH_CONNECTOR",
        "creative_director_agent": (
            "DRAFT_GENERATED_BY_CONFIGURED_LLM"
            if cinematic_pack and cinematic_pack["generation_mode"] == "configured_llm"
            else "DRAFT_GENERATED_RULE_BASED"
        ) if cinematic_pack else ("PLANNED" if brief_ok else "BLOCKED_BRIEF_QUALITY_GATE"),
        "script_agent": "DRAFT_SHOTLIST_GENERATED" if cinematic_pack else (
            "PLANNED" if brief_ok and wants_video else ("NOT_REQUIRED" if brief_ok else "BLOCKED_BRIEF_QUALITY_GATE")),
        "visual_agent": "DRAFT_VISUAL_PROMPTS_GENERATED" if cinematic_pack else (
            "PLANNED" if brief_ok else "BLOCKED_BRIEF_QUALITY_GATE"),
        "motion_agent": "BLOCKED_NO_RENDERER" if wants_video else "NOT_REQUIRED",
        "sound_agent": "DRAFT_DIRECTION_GENERATED" if cinematic_pack else (
            "PLANNED" if brief_ok and wants_video else ("NOT_REQUIRED" if brief_ok else "BLOCKED_BRIEF_QUALITY_GATE")),
        "editor_agent": "BLOCKED_PENDING_RENDERED_SHOTS" if wants_video else "NOT_REQUIRED",
        "quality_agent": "BLOCKED_UNTIL_ACTUAL_EXPORT_EXISTS" if wants_video else "BLOCKED_PENDING_MEDIA",
        "approval_agent": "BLOCKED_PENDING_QUALITY_REVIEW",
        "publishing_agent": "BLOCKED_PENDING_CLIENT_APPROVAL_AND_INTEGRATION",
    }
    tasks = [{"agent": name, "purpose": purpose, "depends_on": deps, "status": statuses[name]}
             for name, purpose, deps in AGENTS]
    pid = hashlib.sha256((order["work_order_id"] + "|creative_agent_pipeline_v2").encode()).hexdigest()[:16]
    llm_used = bool(cinematic_pack and cinematic_pack["execution_truth"]["llm_inference_used"])
    return {
        "schema_version": "creative_agent_pipeline_v2",
        "pipeline_id": pid,
        "client": order["client"],
        "work_order": order,
        "cinematic_ad_pack": cinematic_pack,
        "agent_tasks": tasks,
        "execution_truth": {
            "rule_based_creative_plan_generated": bool(cinematic_pack and cinematic_pack["generation_mode"] == "deterministic_industry_routes"),
            "external_llm_used": llm_used,
            "public_research_performed": False,
            "image_rendered": False,
            "video_rendered": False,
            "audio_rendered": False,
            "quality_review_of_rendered_media_performed": False,
            "client_approval_received": False,
            "published": False,
            "payment_processed": False,
        },
        "blockers": [
            "Connect a public research tool to perform and cite competitor research.",
            "Connect and test an approved image generator and image-to-video renderer.",
            "Add editing and rights-cleared audio workflow.",
            "Quality-check actual rendered exports; text-only checks are insufficient.",
            "Require explicit client approval before publishing or spending.",
        ],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--output", default="artifacts/creative-agent-pipeline.json")
    parser.add_argument("--use-llm", action="store_true",
                        help="Use configured local/explicitly enabled LLM; fail rather than silently falling back")
    args = parser.parse_args()
    try:
        brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        report = build_agent_pipeline(brief, use_llm=args.use_llm)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PLANNED_WITH_BLOCKERS", "pipeline_id": report["pipeline_id"],
                          "agent_count": len(report["agent_tasks"]),
                          "creative_pack_created": report["cinematic_ad_pack"] is not None,
                          "external_llm_used": report["execution_truth"]["external_llm_used"],
                          "video_rendered": False, "published": False, "output": str(out)}))
        return 0
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "error": str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
