"""Build a high-detail, client-specific cinematic ad production pack.

This creates prompts and a shot plan, not rendered media. All on-image text is
planned for a later editor pass to preserve spelling and legibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from agents.creative_work_order import validate_client_brief

VERSION = "cinematic_ad_pack_v1"

ROUTES = {
    "salon": [
        ("Macro-to-makeover", "An extreme hair or beauty-detail opening transforms into a polished final look.",
         "macro_detail", "slow orbit with controlled strands and light movement", "Beauty is a detail-by-detail experience."),
        ("Tools in motion", "Approved salon tools and products move in a carefully choreographed product ballet.",
         "tool_choreography", "precise object motion around a stable subject, no chaotic particle storm", "Every detail has a purpose."),
        ("Mirror reveal", "A consent-approved subject moves from preparation to a confident mirror reveal.",
         "mirror_reveal", "gentle push-in, natural movement, match-cut into the final look", "Make the moment yours."),
    ],
    "beauty_parlour": [
        ("Macro-to-makeover", "A close detail of the actual service leads into a polished result.",
         "macro_detail", "soft orbit, controlled lighting shift, natural skin and hair texture", "Beauty lives in the details."),
        ("Tools in motion", "Actual service tools and products form a choreographed visual around the service.",
         "tool_choreography", "slow precise orbit; keep labels and product shapes stable", "Carefully crafted for you."),
        ("Mirror reveal", "A consent-approved final look is revealed in a cinematic mirror moment.",
         "mirror_reveal", "gentle push-in and a smooth match cut, no facial identity drift", "Your look. Your moment."),
    ],
    "auto_parts": [
        ("Precision exploded view", "The actual supplied part is shown in a controlled exploded-view sequence, then aligns.",
         "mechanical_exploded_view", "parts separate and reassemble along mechanically plausible paths", "Precision in every part."),
        ("Workshop macro", "Start on metal finish, fasteners and real product details before showing the part in context.",
         "macro_engineering", "macro rack focus, restrained metallic highlights, stable part geometry", "Details built for the job."),
        ("Fitment-to-finish", "A qualified mechanic shows the supplied part in an appropriate workshop context, then the finished vehicle.",
         "installation_sequence", "match cuts between part, hands and vehicle; do not invent compatibility", "The right part starts here."),
    ],
    "auto parts store": [
        ("Precision exploded view", "Actual products separate in a controlled engineering-inspired composition, then align.",
         "mechanical_exploded_view", "precise part movement with stable geometry and clean background", "Precision in every part."),
        ("Workshop macro", "Metal, machining and true product features lead the story.",
         "macro_engineering", "macro rack focus and controlled highlights", "See the detail. Know the part."),
        ("Store-to-road", "Start at real shelves, feature the chosen part, finish with a suitable vehicle context.",
         "store_to_product", "smooth aisle push-in and match cut; no unsupported performance claims", "Find the part you need."),
    ],
    "restaurant": [
        ("Sensory close-up", "Steam, texture and plating details build appetite before the dish reveal.",
         "food_macro", "slow macro dolly, gentle steam, warm practical highlights", "Let the details speak."),
        ("Craft in motion", "A real preparation step becomes a rhythmic kitchen sequence.",
         "chef_process", "paced cuts, plausible hand and utensil movement", "Made with care, served with character."),
        ("Table moment", "The finished dish arrives at a real table, with a human moment if permission is confirmed.",
         "shared_table", "smooth reveal and small natural gestures", "Make room for a good moment."),
    ],
    "cafe": [
        ("First-pour cinema", "Coffee or the actual signature drink is introduced through texture and pour detail.",
         "beverage_macro", "macro push-in, liquid movement only when physically plausible", "A small moment, made special."),
        ("Craft ritual", "The real preparation process becomes an elegant mini-story.",
         "barista_process", "steady close-ups, measured movement, rhythmic match cuts", "Your daily ritual, reimagined."),
        ("Inside the cafe", "Move from a real space detail to a drink and a welcoming customer moment.",
         "space_to_product", "slow gimbal-like move and gentle rack focus", "Come in. Make it your moment."),
    ],
    "general store": [
        ("Aisle-to-hero", "Move through the actual store and end on selected real products.",
         "store_walkthrough", "smooth forward camera move, controlled shelf parallax", "Everyday needs, thoughtfully chosen."),
        ("Product constellation", "A curated set of actual products gets a clean, controlled hero reveal.",
         "product_hero", "slow orbit with separate products staying true to supplied references", "Discover your everyday essentials."),
        ("Shopping moment", "A real store journey ends with a helpful product selection.",
         "customer_journey", "natural movement and practical framing, subject consent required", "Your essentials, all in one stop."),
    ],
    "retail": [
        ("Aisle-to-hero", "The real store becomes a smooth visual journey ending on selected products.",
         "store_walkthrough", "steady forward move and clean rack focus", "Discover what fits your day."),
        ("Product constellation", "Selected actual products take center stage in a polished hero arrangement.",
         "product_hero", "restrained orbit and precise product movement", "Small details. Smart choices."),
        ("Shopping moment", "Show a practical customer journey using approved store imagery.",
         "customer_journey", "natural motion and clean transitions, no fabricated endorsements", "Make every visit count."),
    ],
    "local service": [
        ("Problem-to-process", "Show the real job context, then the skilled process and completed work.",
         "process_reveal", "steady detail shots, clear match cuts, no fabricated before/after", "See the care behind the work."),
        ("Tools and craft", "Use authentic tools and workmanship as the visual hero.",
         "craft_macro", "controlled macro focus and purposeful hand movement", "Good work shows in the details."),
        ("People behind the service", "Introduce the approved team, process and clear next step.",
         "team_story", "natural handheld-gimbal feel, only people with permission", "A real team. A clear next step."),
    ],
}

DEFAULT_ROUTES = [
    ("Detail-to-hero", "Open with the most distinctive real feature of the offer, then reveal it in context.",
     "detail_hero", "slow macro push-in and deliberate focus transition", "Look closer."),
    ("Process reveal", "Tell a concise story through the real process behind the product or service.",
     "process_story", "controlled match cuts and natural object movement", "See how it comes together."),
    ("Real-world payoff", "Show the actual product or service in a relevant, credible use context.",
     "use_case", "smooth camera move and restrained transition into the final frame", "Take the next step."),
]

def _industry_routes(business_type: str):
    value = re.sub(r"[^a-z0-9]+", " ", business_type.lower()).strip()
    for key, routes in ROUTES.items():
        if key in value or value in key:
            return routes
    if any(word in value for word in ("salon", "hair", "beauty", "parlour", "parlor", "spa")):
        return ROUTES["salon"]
    if any(word in value for word in ("auto", "car part", "motor part", "mechanic", "garage")):
        return ROUTES["auto parts"]
    if any(word in value for word in ("shop", "store", "retail", "grocery", "supermarket")):
        return ROUTES["retail"]
    if any(word in value for word in ("food", "dining", "restaurant")):
        return ROUTES["restaurant"]
    if any(word in value for word in ("coffee", "cafe", "café")):
        return ROUTES["cafe"]
    if any(word in value for word in ("service", "repair", "plumber", "electrician", "cleaning")):
        return ROUTES["local service"]
    return DEFAULT_ROUTES

def _build_shots(client_name: str, business_type: str, topic: str, audience: str, goal: str,
                 cta: str, route: tuple[str, str, str, str, str], reference_notes: list[str]) -> list[dict[str, Any]]:
    title, narrative, mechanic, motion, payoff = route
    context = "; ".join(reference_notes[:3]) if reference_notes else "Use only supplied, approved client assets."
    scenes = [
        ("0-2s", "Pattern interrupt", f"Extreme detail of the real {topic} relevant to {business_type}; immediate visual intrigue.",
         f"Vertical 9:16 cinematic macro of the actual client-provided {topic}, grounded in {business_type}. {context}. Realistic materials, crisp focus, premium commercial lighting. No generated lettering, no fake logos, no additional products."),
        ("2-6s", "Signature motion", f"{narrative} Keep the supplied product, person and brand details consistent.",
         f"Continue the same {business_type} campaign and exact reference subject. Visual mechanic: {mechanic}. One clear focal action, realistic physics, consistent shape, colour and identity. Keep composition vertical 9:16. No text or logo hallucinations."),
        ("6-13s", "Credible proof / payoff", f"Show a truthful use or process detail relevant to {audience} and {goal}; use only approved facts.",
         f"Show the actual approved product/service in a plausible real context. Camera motion: {motion}. Premium but believable commercial look, natural texture, true-to-reference details, no unsupported results, no invented awards or testimonials. No embedded text."),
        ("13-18s", "Brand end frame", f"Hold on an elegant hero frame with space for the real logo and the CTA: {cta}.",
         f"Create a clean final hero composition for {client_name} in vertical 9:16, with clear negative space for editor-added approved logo and CTA. Do not render text or a fake logo. Keep product details faithful to reference."),
    ]
    return [{"time": t, "purpose": purpose, "scene_direction": direction, "visual_prompt": visual,
             "motion_prompt": motion if idx == 1 else (
                 "Very slow camera push-in with subtle natural environmental movement; preserve product and subject identity."
                 if idx == 0 else
                 "Use one controlled camera move, realistic physics, stable geometry and consistent identity; avoid flicker, morphing and invented details."
                 if idx == 2 else
                 "Slow, elegant camera settle; keep clear negative space for typography added in post.")
            } for idx, (t, purpose, direction, visual, motion) in enumerate(scenes)]

def build_cinematic_ad_pack(raw_brief: dict[str, Any]) -> dict[str, Any]:
    brief = validate_client_brief(raw_brief)
    client = brief["client_name"]
    business = brief["business_type"]
    topic = brief["offer_or_topic"]
    routes = _industry_routes(business)
    concepts = []
    for idx, route in enumerate(routes, start=1):
        title, narrative, mechanic, motion, payoff = route
        concepts.append({
            "concept_id": f"route_{idx}",
            "title": title,
            "story": narrative,
            "visual_mechanic": mechanic,
            "difference_from_other_routes": payoff,
            "hook": f"{topic}: {payoff}",
            "shots": _build_shots(client, business, topic, brief["audience"], brief["goal"],
                                  brief["call_to_action"], route, brief["reference_notes"]),
            "audio_direction": "Purposeful original sound design; choose a properly licensed or original track after client review.",
            "deliverable_target": {"aspect_ratio": "9:16", "duration_seconds": 18, "export": "1080x1920 target; verify source/render capabilities"},
        })
    claim_text = json.dumps(concepts, ensure_ascii=False).lower()
    prohibited = [claim.lower() for claim in brief["prohibited_claims"] if claim.lower() in claim_text]
    checks = {
        "three_routes_created": len(concepts) == 3,
        "route_titles_are_distinct": len({x["title"] for x in concepts}) == 3,
        "each_route_has_four_timed_shots": all(len(x["shots"]) == 4 for x in concepts),
        "all_routes_have_distinct_visual_mechanics": len({x["visual_mechanic"] for x in concepts}) == 3,
        "text_is_editor_added_not_baked_into_generated_images": all(
            "No generated lettering" in x["shots"][0]["visual_prompt"] and
            "Do not render text" in x["shots"][3]["visual_prompt"] for x in concepts),
        "no_user_prohibited_claims_found": not prohibited,
    }
    brief_hash = hashlib.sha256(json.dumps(brief, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return {
        "schema_version": VERSION,
        "pack_id": brief_hash[:16],
        "client": {"name": client, "business_type": business, "audience": brief["audience"], "goal": brief["goal"]},
        "creative_strategy": {"reference_style": "cinematic, high-detail, original concept; do not copy any named ad",
                              "source_of_differentiation": "industry-specific visual mechanics, real client assets, distinct story structures",
                              "approved_facts_only": brief["approved_facts"]},
        "concepts": concepts,
        "quality_gate": {"checks": checks, "prohibited_claim_hits": prohibited,
                         "status": "DRAFT_REVIEW_REQUIRED" if all(checks.values()) else "HOLD_FOR_REVIEW",
                         "rendered_assets_verified": False},
        "execution_truth": {"research_performed": False, "llm_inference_used": False, "image_rendered": False,
                            "video_rendered": False, "audio_rendered": False, "published": False},
        "next_steps": ["Choose a concept route", "Confirm photo/video rights and approved facts",
                       "Generate or select reference stills with an approved tool", "Animate shots with a connected renderer",
                       "Edit typography, logo, subtitles and audio in post", "Inspect actual exports before client delivery"],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--output", default="artifacts/cinematic-ad-pack.json")
    args = parser.parse_args()
    try:
        brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        pack = build_cinematic_ad_pack(brief)
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": pack["quality_gate"]["status"], "pack_id": pack["pack_id"],
                          "concepts": len(pack["concepts"]), "rendered": False, "output": str(path)}))
        return 0 if pack["quality_gate"]["status"] == "DRAFT_REVIEW_REQUIRED" else 1
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "error": str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
