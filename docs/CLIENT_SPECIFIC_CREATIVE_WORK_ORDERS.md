# Client-Specific Creative Work Orders

## What it covers

The planner accepts a required client brief and one or more work types: brand strategy, social content, Reel/video storyboard, poster art direction, website build, app build, original music concept, blog/SEO article, billing system specification, social media management, and product launch. Each requested type gets a different deliverable schema. The output adapts its creative direction to the client's business type, audience, goal, offer/topic, voice, palette, platforms and prohibited claims.

## Example brief

    {
      "client_name": "Bluebird Cafe",
      "business_type": "cafe",
      "audience": "students and remote workers",
      "goal": "increase weekday visits",
      "offer_or_topic": "quiet coffee break with a pastry",
      "brand_voice": "friendly and thoughtful",
      "call_to_action": "Ask about today's menu",
      "platforms": ["instagram", "facebook"],
      "work_types": ["social_content", "reel_video", "poster_design", "social_media_management"],
      "approved_facts": ["quiet coffee break with a pastry"],
      "prohibited_claims": ["cheapest in town"],
      "brand_colors": ["navy", "cream"],
      "reference_notes": ["Client-supplied visual references, after permission"]
    }

Run it:

    python -m agents.creative_work_order --brief client-brief.json --output artifacts/creative-work-order.json

## No copy-paste creative rule

The planner produces distinct concept angles and deliverable structures, but these are still text plans—not finished HD posters, rendered video, generated music, a working website or a released app. Do not sell the JSON as a finished creative asset. Real production needs approved media-generation/build tools, client assets and rights, device/render checks, and a human review. A new client brief should be created for each client; never reuse one client's private data for another client.

## Professional quality gates

- Required brief fields and supported task types are validated.
- Client-approved facts and prohibited claims are tracked.
- Poster plans include platform sizing/safe-zone guidance and mobile/200% readability checks.
- Video plans include timing, original/licensed audio guidance and consent/rights checks.
- Website/app plans include accessibility, security, testing and release gates.
- Billing plans separate invoice workflow from real payment processing and require review.
- Publishing, deployment, payment and customer delivery remain blocked in this planner.
- A high score never overrides a factuality, safety, copyright or permission failure.
