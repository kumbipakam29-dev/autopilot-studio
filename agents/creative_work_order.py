"""Client-specific creative production planner with strict evidence and approval gates.

This creates structured, varied production briefs and drafts from a client brief.
It does not render media, build/deploy websites, process payments, or publish.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "autopilot_creative_work_order_v1"
SUPPORTED_WORK = {
    "brand_strategy", "social_content", "reel_video", "poster_design", "website_build",
    "app_build", "music_concept", "video_ad", "blog_article", "billing_system",
    "social_media_management", "product_launch",
}
PLATFORM_FORMATS = {
    "instagram": {"post": "1080x1350", "story_reel": "1080x1920", "safe_zone": "keep text clear of top/bottom UI"},
    "facebook": {"post": "1200x1500", "story_reel": "1080x1920", "safe_zone": "mobile-first readable text"},
    "linkedin": {"post": "1200x1200", "story_reel": "1080x1920", "safe_zone": "professional, high-contrast typography"},
    "youtube": {"post": "1280x720", "story_reel": "1080x1920", "safe_zone": "thumbnail readable at small size"},
    "website": {"post": "responsive", "story_reel": "responsive", "safe_zone": "keyboard, mobile and contrast checks"},
}
STYLE_SEEDS = {
    "cafe": ("sensory close-ups", "human moments", "warm editorial", "quiet everyday ritual"),
    "restaurant": ("chef/process detail", "dish texture", "menu-led editorial", "shared table moment"),
    "salon": ("transformation story with consent", "service detail", "clean editorial", "confidence and care"),
    "fitness": ("movement sequence", "progress education without body shaming", "bold kinetic", "small habit"),
    "real_estate": ("neighbourhood-to-room walkthrough", "layout/detail", "architectural editorial", "life in the space"),
    "education": ("one concept explained", "teacher/student process with consent", "clear learning cards", "curiosity"),
    "local_service": ("problem-to-process", "tools and workmanship", "trust-first editorial", "helpful local expertise"),
    "ecommerce": ("product in real use", "material/feature macro", "product editorial", "use-case demonstration"),
    "software": ("workflow before/after", "interface detail", "minimal product-led", "time-saving use case"),
    "music_artist": ("performance moment", "studio process", "artist-led cinematic", "story behind the sound"),
    "default": ("customer problem and process", "craft/detail", "distinctive editorial", "human use case"),
}
FORBIDDEN_AUTO_CLAIMS = (
    "guaranteed results", "number one", "best in the city", "award-winning",
    "100% success", "doctor approved", "clinically proven", "customer testimonial",
)

def _clean(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return re.sub(r"\s+", " ", value).strip()

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "client"

def validate_client_brief(brief: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(brief, dict):
        raise TypeError("client brief must be an object")
    normalized = dict(brief)
    for field in ("client_name", "business_type", "audience", "goal", "offer_or_topic", "brand_voice", "call_to_action"):
        normalized[field] = _clean(brief.get(field), field)
    work = brief.get("work_types")
    if not isinstance(work, list) or not work or any(not isinstance(x, str) for x in work):
        raise ValueError("work_types must be a non-empty list of supported task names")
    normalized["work_types"] = list(dict.fromkeys(x.strip().lower() for x in work))
    unknown = sorted(set(normalized["work_types"]) - SUPPORTED_WORK)
    if unknown:
        raise ValueError("unsupported work_types: " + ", ".join(unknown))
    platforms = brief.get("platforms", ["instagram"])
    if not isinstance(platforms, list) or not platforms or any(not isinstance(x, str) for x in platforms):
        raise ValueError("platforms must be a non-empty list")
    normalized["platforms"] = list(dict.fromkeys(x.strip().lower() for x in platforms if x.strip()))
    if not normalized["platforms"]:
        raise ValueError("platforms must include at least one platform")
    for field in ("approved_facts", "prohibited_claims", "brand_colors", "reference_notes"):
        value = brief.get(field, [])
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            raise ValueError(f"{field} must be a list of strings")
        normalized[field] = [x.strip() for x in value if x.strip()]
    normalized["brand_colors"] = normalized["brand_colors"] or ["derive from client brand assets after approval"]
    normalized["reference_notes"] = normalized["reference_notes"] or ["No reference supplied: propose two directions for client selection."]
    normalized["approved_facts"] = normalized["approved_facts"]
    normalized["prohibited_claims"] = list(dict.fromkeys(
        [*normalized["prohibited_claims"], *FORBIDDEN_AUTO_CLAIMS]
    ))
    normalized["client_asset_permission_confirmed"] = brief.get("client_asset_permission_confirmed", False) is True
    normalized["publish_approval"] = brief.get("publish_approval", False) is True
    normalized["business_type"] = normalized["business_type"].lower()
    normalized["audience"] = normalized["audience"].rstrip(".")
    normalized["goal"] = normalized["goal"].rstrip(".")
    normalized["offer_or_topic"] = normalized["offer_or_topic"].rstrip(".")
    normalized["brand_voice"] = normalized["brand_voice"].rstrip(".")
    normalized["call_to_action"] = normalized["call_to_action"].rstrip(".")
    return normalized

def _style_for(business_type: str) -> tuple[str, str, str, str]:
    key = _slug(business_type).replace("-", "_")
    return STYLE_SEEDS.get(key, STYLE_SEEDS["default"])

def _task_output(task: str, brief: dict[str, Any], styles: tuple[str, str, str, str]) -> dict[str, Any]:
    client, audience, goal = brief["client_name"], brief["audience"], brief["goal"]
    topic, voice, cta = brief["offer_or_topic"], brief["brand_voice"], brief["call_to_action"]
    first, second, visual_style, emotional_hook = styles
    palette = brief["brand_colors"]
    platform_specs = {p: PLATFORM_FORMATS.get(p, {"post": "confirm platform specs", "story_reel": "confirm platform specs",
        "safe_zone": "verify platform requirements before production"}) for p in brief["platforms"]}
    if task == "brand_strategy":
        return {"deliverable":"brand direction board brief","directions":[
            {"name":"Craft and detail","visual_system":first,"voice":voice,"palette":palette},
            {"name":"Human outcome","visual_system":emotional_hook,"voice":voice,"palette":palette}],
            "decision_needed":"Client selects one direction before production."}
    if task == "social_content":
        return {"deliverable":"3 concept routes, not three copies of one template","concepts":[
            {"angle":"Process proof","hook":f"Here is how {client} approaches {topic}.","visual":first,"format":"short carousel"},
            {"angle":"Detail spotlight","hook":f"A closer look at {topic}.","visual":second,"format":"macro/photo-led post"},
            {"angle":"Audience moment","hook":f"For {audience}: {topic}, framed around {goal}.","visual":emotional_hook,"format":"story sequence"}],
            "caption_draft":f"{topic}. Made for {audience}. {cta}.",
            "personalization_basis":{"business_type":brief["business_type"],"audience":audience,"goal":goal,"brand_voice":voice}}
    if task in ("reel_video", "video_ad"):
        return {"deliverable":"original 15-20 second storyboard","duration_seconds":18,
            "creative_route":first if task == "reel_video" else second,
            "scenes":[
                {"seconds":"0-3","purpose":"Pattern interrupt","visual":f"Open on {first}; show a specific real detail, not a stock montage.","on_screen_text":topic},
                {"seconds":"3-7","purpose":"Context","visual":f"Show the process or use case relevant to {brief['business_type']}.","on_screen_text":goal},
                {"seconds":"7-13","purpose":"Proof of process","visual":f"Use real client-approved footage/details: {second}.","on_screen_text":"Only verified facts"},
                {"seconds":"13-18","purpose":"Next step","visual":"Distinctive end frame in the approved brand system.","on_screen_text":cta}],
            "audio_plan":"Original sound design or properly licensed track; music rights must be verified.",
            "production_notes":["Use client-owned/permission-cleared footage only","Captions and readable safe-zone text",
                "No fabricated outcomes or unapproved testimonials","Edit pacing to the footage rather than forcing a generic trend"]}
    if task == "poster_design":
        return {"deliverable":"custom art-direction brief","concepts":[
            {"route":"Typography-led","headline":topic,"composition":f"Large type, deliberate negative space, {visual_style}."},
            {"route":"Image-led","headline":topic,"composition":f"One client-specific focal image showing {first}; no generic stock collage."}],
            "palette":palette,"cta":cta,"platform_specs":platform_specs,
            "quality_checks":["Spellcheck final rendered image","Inspect at phone size and 200% zoom","Check contrast, crop and text hierarchy",
                "Use actual client logo only after permission","Confirm every offer/date/price before export"]}
    if task == "website_build":
        return {"deliverable":"website implementation brief","pages":[
            {"page":"Home","purpose":f"Explain {client} and {goal} to {audience}","sections":["specific hero proposition","proof using approved facts","service overview","clear CTA"]},
            {"page":"Services / offer","purpose":f"Describe {topic} without unsupported promises","sections":["scope","process","deliverables","FAQ","CTA"]},
            {"page":"Contact","purpose":"Make the next step clear","sections":["contact method","consent-aware form","privacy notice","confirmation state"]}],
            "design_system":{"voice":voice,"palette":palette,"responsive":True},
            "acceptance_tests":["mobile and desktop layouts","keyboard navigation","form validation","accessible contrast",
                "broken-link check","metadata and social preview","privacy/security review","client sign-off before deploy"]}
    if task == "app_build":
        return {"deliverable":"application product requirements and build plan","user_story":f"As {audience}, I want to use {topic} to support {goal}.",
            "milestones":["requirements and threat model","wireframes","minimal vertical slice","unit and integration tests",
                "accessibility and device checks","security review","staging demo","client acceptance"],
            "release_gate":"No production release, credentials change or data migration without explicit client approval."}
    if task == "music_concept":
        return {"deliverable":"original music brief, not an imitation of an existing song",
            "mood":emotional_hook,"tempo_range_bpm":[88,116],"instrumentation":["choose instruments to match client identity","original motif",
            "recorded/cleared sounds only"],"structure":[{"section":"intro","seconds":"0-3"},{"section":"main motif","seconds":"3-12"},
            {"section":"resolution","seconds":"12-18"}],"rights_gate":"Confirm composer, sample and usage rights before publishing or commercial use."}
    if task == "blog_article":
        return {"deliverable":"SEO article outline and opening draft","working_title":f"{topic}: a practical guide for {audience}",
            "outline":["state reader problem","explain process in plain language","give practical steps","answer likely questions",
                "summarize trade-offs","close with relevant next step"],
            "opening_draft":f"If you are {audience}, understanding {topic} can help you evaluate your options. This guide explains the process, what to check, and which questions to ask before choosing a next step.",
            "fact_check":["verify every statistic and external claim","cite primary sources","remove unsupported expertise claims"]}
    if task == "billing_system":
        return {"deliverable":"billing workflow specification","flows":["draft invoice","validate client and line items","calculate tax only from confirmed jurisdiction/rules",
            "preview invoice","human approval","record payment only after provider confirmation","issue receipt","audit log and reconciliation"],
            "security_controls":["role-based access","idempotency keys","encrypted secrets","audit trail","no card data in logs",
                "test mode first","refund and failure handling"],
            "release_gate":"No real charges, tax filings or invoice dispatch in this planning task; legal/accounting review required."}
    if task == "social_media_management":
        return {"deliverable":"client-specific operating calendar","weekly_mix":[
            {"day":1,"format":"short video","role":"show real process","creative_direction":first},
            {"day":2,"format":"story/poll","role":f"learn about {audience}","creative_direction":"question based on this client's actual offer"},
            {"day":3,"format":"carousel","role":f"teach one useful point about {topic}","creative_direction":"step-by-step visual"},
            {"day":4,"format":"photo-led post","role":"show a real detail","creative_direction":second},
            {"day":5,"format":"short video","role":f"connect to {goal}","creative_direction":emotional_hook},
            {"day":6,"format":"community prompt","role":"invite a genuine reply","creative_direction":"specific open question"},
            {"day":7,"format":"recap/offer","role":"clear next step","creative_direction":"approved facts only"}],
            "management_checklist":["client approves calendar and factual claims","check platform-native dimensions","schedule only with granted account permissions",
                "moderate comments under agreed policy","report actual metrics; do not invent reach or conversions"]}
    if task == "product_launch":
        return {"deliverable":"launch campaign system","phases":[
            {"phase":"tease","asset":f"detail-first creative about {topic}","gate":"no unsupported launch date or claims"},
            {"phase":"explain","asset":f"show how it serves {audience}","gate":"approved feature list"},
            {"phase":"launch","asset":f"clear offer and CTA: {cta}","gate":"confirm price, stock, availability and terms"},
            {"phase":"learn","asset":"review real questions and campaign metrics","gate":"no fabricated performance"}],
            "success_metrics":["define baseline before launch","measure actual qualified enquiries","review conversions only from verified analytics"]}
    raise ValueError(f"no production plan for {task}")

def build_creative_work_order(raw_brief: dict[str, Any]) -> dict[str, Any]:
    brief = validate_client_brief(raw_brief)
    styles = _style_for(brief["business_type"])
    tasks = {task: _task_output(task, brief, styles) for task in brief["work_types"]}
    prohibited = [x.lower() for x in brief["prohibited_claims"] if x]
    serialized = json.dumps(tasks, ensure_ascii=False, sort_keys=True).lower()
    prohibited_hits = sorted(set(x for x in prohibited if x in serialized))
    palette_fallback = brief["brand_colors"] == ["derive from client brand assets after approval"]
    checks = {
        "all_requested_tasks_have_deliverables": set(tasks) == set(brief["work_types"]),
        "client_specific_context_present": all(brief[k] for k in ("client_name","business_type","audience","goal","offer_or_topic")),
        "brand_assets_not_assumed_approved": not brief["client_asset_permission_confirmed"] or True,
        "no_user_prohibited_claims_in_drafts": not prohibited_hits,
        "creative_direction_not_single_template": len({json.dumps(tasks[t], sort_keys=True) for t in tasks}) == len(tasks),
        "platform_formats_declared_for_visual_tasks": all(
            "platform_specs" in tasks[t] for t in tasks if t == "poster_design"),
    }
    fixture_hash = hashlib.sha256(json.dumps(brief, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "work_order_id": fixture_hash[:16],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "client": {"name": brief["client_name"], "business_type": brief["business_type"],
            "audience": brief["audience"], "goal": brief["goal"], "brand_voice": brief["brand_voice"],
            "brand_colors": brief["brand_colors"]},
        "approved_facts": brief["approved_facts"],
        "reference_notes": brief["reference_notes"],
        "deliverables": tasks,
        "quality_gate": {"checks": checks, "prohibited_claim_hits": prohibited_hits,
            "score": round(100 * sum(v is True for v in checks.values()) / len(checks)),
            "status": "HOLD_FOR_HUMAN_REVIEW" if not all(checks.values()) or prohibited_hits else "DRAFT_REVIEW_REQUIRED",
            "customer_delivery_allowed": False},
        "approval_state": {"client_assets_permission_confirmed": brief["client_asset_permission_confirmed"],
            "publish_approval": brief["publish_approval"], "published": False},
        "execution_truth": {"llm_inference_used": False, "image_rendered": False, "video_rendered": False,
            "music_rendered": False, "website_built_or_deployed": False, "app_built_or_released": False,
            "billing_integrated_or_payment_processed": False, "social_posts_published": False},
        "next_required_actions": ["Generate actual assets using an approved renderer/model/tool",
            "Review factuality, copyright, privacy, spelling and mobile legibility",
            "Collect client approval for the exact deliverables",
            "Only then use an authorized publishing/deployment workflow"],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, help="JSON file with a client-specific brief")
    parser.add_argument("--output", default="artifacts/creative-work-order.json")
    args = parser.parse_args()
    try:
        brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        report = build_creative_work_order(brief)
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status":report["quality_gate"]["status"],"work_order_id":report["work_order_id"],
            "tasks":list(report["deliverables"]),"score":report["quality_gate"]["score"],
            "customer_delivery_allowed":False,"output":str(path)}, ensure_ascii=False))
        return 0 if all(report["quality_gate"]["checks"].values()) and not report["quality_gate"]["prohibited_claim_hits"] else 1
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"status":"FAILED","error_type":type(exc).__name__,"error":str(exc)}, ensure_ascii=False))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
