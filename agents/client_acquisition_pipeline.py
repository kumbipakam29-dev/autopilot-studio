"""Offline client-acquisition draft pipeline composed from specialist capabilities.

This orchestrator uses only facts supplied by the user. It does not browse for leads,
send outreach, publish content, or claim that fictional spec work is real client work.
"""
from __future__ import annotations

from typing import Any

from agents.specialist_capabilities import run_capability

PIPELINE_VERSION = "0.1.0"


def build_client_acquisition_pack(data: dict[str, Any]) -> dict[str, Any]:
    """Return a review-ready starter pack for one supplied small-business brief."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")

    brief_result = run_capability("APS-SM-04", data)
    brief = brief_result["brief"]
    business_type = str(brief.get("business_type") or "local service business")
    business_name = str(brief.get("business_name") or "Sample Business")
    audience = str(brief.get("audience") or "local customers")
    offer = str(brief.get("offer") or "the service")
    platforms = brief.get("platforms") or ["Instagram"]
    if isinstance(platforms, str):
        platforms = [platforms]

    niche = run_capability("APS-CR-01", {
        "business_type": business_type,
        "location": brief.get("location", ""),
        "facts": data.get("facts", []),
        "services": data.get("services", [offer]),
    })
    captions = run_capability("APS-SM-05", {
        "business_name": business_name,
        "audience": audience,
        "offer": offer,
        "benefit": data.get("benefit", ""),
        "call_to_action": brief.get("call_to_action", "Message us to learn more"),
    })
    calendar = run_capability("APS-CR-02", {
        "business_name": business_name,
        "business_type": business_type,
        "audience": audience,
        "offer": offer,
        "platforms": platforms,
    })
    reels = [
        run_capability("APS-CR-03", {
            "topic": topic,
            "audience": audience,
            "call_to_action": brief.get("call_to_action", "Save this for later"),
        })
        for topic in (offer, data.get("reel_topic_2", f"one tip about {offer}"))
    ]
    portfolio = run_capability("APS-CR-04", {
        "business_type": business_type,
        "concept": data.get("portfolio_concept", offer),
    })
    outreach_input = {
        "business_name": business_name,
        "specific_public_fact": data.get("specific_public_fact", ""),
        "service_offer": data.get("service_offer", "social media content support"),
        "sender_name": data.get("sender_name", "AutoPilot Digital Studio"),
    }
    outreach = run_capability("APS-CR-05", outreach_input)

    missing = list(brief_result["missing_fields"])
    if not data.get("specific_public_fact"):
        missing.append("specific_public_fact_for_outreach")
    return {
        "pipeline_version": PIPELINE_VERSION,
        "status": "draft_pack_ready_for_human_review",
        "business_name": business_name,
        "brief": brief_result,
        "niche_hypotheses": niche,
        "caption_drafts": captions,
        "seven_day_calendar": calendar,
        "reel_scripts": reels,
        "portfolio_spec_work": portfolio,
        "outreach_draft": outreach,
        "missing_inputs": missing,
        "safety": {
            "uses_user_supplied_facts_only": True,
            "live_prospect_research_performed": False,
            "external_sources_fetched": False,
            "outreach_sent": False,
            "content_published": False,
            "portfolio_is_fictional_spec_work": True,
            "client_or_revenue_claims_made": False,
            "human_review_required": True,
        },
    }
