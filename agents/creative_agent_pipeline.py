"""Auditable handoff plan for client-specific cinematic ad production.

Plans agent responsibilities only. No external model, media rendering, account access,
publishing, or payment is performed by this module.
"""
import argparse
import hashlib
import json
from pathlib import Path
from agents.creative_work_order import build_creative_work_order

AGENTS = [
    ("intake_agent", "Validate brief, approved facts and asset permissions", []),
    ("research_agent", "Find cited public competitor patterns; do not copy", ["intake_agent"]),
    ("creative_director_agent", "Develop distinct client-specific campaign concepts", ["intake_agent", "research_agent"]),
    ("script_agent", "Write hook, shot list, voiceover, on-screen copy and CTA", ["creative_director_agent"]),
    ("visual_agent", "Specify framing, lighting, product fidelity and brand style", ["creative_director_agent"]),
    ("motion_agent", "Animate approved stills with controlled camera and subject motion", ["visual_agent"]),
    ("sound_agent", "Plan sound design and verify music rights", ["script_agent"]),
    ("editor_agent", "Assemble shots, pacing, captions and platform exports", ["script_agent", "motion_agent", "sound_agent"]),
    ("quality_agent", "Check factuality, originality, legibility, fidelity and technical quality", ["editor_agent", "visual_agent"]),
    ("approval_agent", "Package previews and collect explicit client approval", ["quality_agent"]),
    ("publishing_agent", "Publish only after approval through authorized integrations", ["approval_agent"]),
]

def build_agent_pipeline(brief):
    order = build_creative_work_order(brief)
    brief_ok = order["quality_gate"]["status"] == "DRAFT_REVIEW_REQUIRED"
    tasks = []
    for name, purpose, deps in AGENTS:
        if name == "research_agent":
            status = "BLOCKED_NO_RESEARCH_CONNECTOR"
        elif name == "motion_agent":
            status = "BLOCKED_NO_RENDERER"
        elif name in ("editor_agent", "quality_agent", "approval_agent", "publishing_agent"):
            status = "BLOCKED_PENDING_UPSTREAM_OUTPUTS"
        elif name in ("script_agent", "visual_agent", "sound_agent", "creative_director_agent", "intake_agent"):
            status = "PLANNED" if brief_ok else "BLOCKED_BRIEF_QUALITY_GATE"
        else:
            status = "BLOCKED_PENDING_APPROVAL"
        tasks.append({"agent": name, "purpose": purpose, "depends_on": deps, "status": status})
    pid = hashlib.sha256((order["work_order_id"] + "|creative_agent_pipeline_v1").encode()).hexdigest()[:16]
    return {
        "schema_version": "creative_agent_pipeline_v1",
        "pipeline_id": pid,
        "client": order["client"],
        "work_order": order,
        "agent_tasks": tasks,
        "execution_truth": {"research_performed": False, "external_llm_used": False,
            "image_rendered": False, "video_rendered": False, "audio_rendered": False,
            "quality_review_of_rendered_media_performed": False, "client_approval_received": False,
            "published": False, "payment_processed": False},
        "blockers": ["Connect a public research tool", "Connect and test approved image/video renderers",
            "Add editing and rights-cleared audio workflow", "Quality-check actual rendered files",
            "Require explicit client approval before publishing or spending"],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--output", default="artifacts/creative-agent-pipeline.json")
    args = parser.parse_args()
    try:
        brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        report = build_agent_pipeline(brief)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
        print(json.dumps({"status": "PLANNED_WITH_BLOCKERS", "pipeline_id": report["pipeline_id"],
                          "agent_count": len(report["agent_tasks"]), "video_rendered": False,
                          "published": False, "output": str(out)}))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "error": str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
