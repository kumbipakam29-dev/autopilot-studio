# Cinematic Product Ad Pipeline — Watch Benchmark

Status: **production specification only; no motion footage has been generated or validated by this document.**

Purpose: establish a repeatable, quality-gated workflow for AutoPilot Studio to create cinematic product ads (starting with a fictional, unbranded watch) and later adapt the workflow to salons, auto-parts shops, cafes, and other small businesses.

## Non-negotiable output standard

The target is a true motion ad, not a slideshow:
- The subject visibly moves inside each clip (moving parts, hand/body motion, atmospheric motion), and the camera has deliberate movement.
- Keep one identifiable watch design across shots. Do not invent, mutate, or unreadably redraw a logo, dial text, hands, crown, or strap.
- Use 9:16 vertical framing for a short-form social ad, 1080 × 1920 final canvas where source quality supports it, and readable safe margins.
- Put exact brand, price, CTA, and legal copy on top in the editor after generation. Do not rely on generative models to render final typography.
- Avoid cloning any existing brand ad, trademark, protected character, suit design, or recognizable franchise scene. The transformation is an original precision-mechanical exosuit motif, not an Iron Man replica.
- Never label a storyboard, keyframe board, animated still, or slideshow as a finished motion video.

## Concept

**Working title:** TIME / TAKE FLIGHT  
**Product:** fictional unbranded premium mechanical watch  
**Duration:** 18–20 seconds  
**Structure:** precision → assembly → human transformation → flight → hero reveal  
**Tone:** dark graphite, brushed steel, restrained champagne highlights, physically plausible materials, premium lighting, high contrast without crushed detail.

## Shot list and generation prompts

Generate each shot as an individual 3–5 second clip. Use the same approved watch reference image wherever the tool supports reference-to-video. If the product changes shape or details, reject the clip instead of hiding the error with transitions.

### Shot 1 — The mechanism wakes (0:00–0:03)
**Prompt:** “Vertical 9:16 macro cinematic product film of a fictional unbranded luxury mechanical wristwatch movement floating in a dark graphite studio. Tiny polished-steel and champagne-gold gears begin rotating at different speeds; the balance wheel oscillates rhythmically; a few precision components hover a short distance above their sockets. Camera performs a slow, controlled macro dolly-in with shallow depth of field and a single narrow strip of light moving across the metal. Physically plausible mechanics, premium materials, crisp micro-detail, restrained particles, no text, no logo, stable composition, one continuous shot.”

### Shot 2 — Parts assemble (0:03–0:06)
**Prompt:** “Continue the same fictional watch design and graphite/champagne palette. A small number of visible watch components move with precise magnetic alignment into the watch case: gear train settles, case ring closes, crown aligns, glass lowers last. Every component travels on a clear, deliberate path; no liquid-metal morphing, no random extra parts. Camera makes a slow quarter-orbit around the watch, smooth motion, realistic inertia, premium macro lighting, single continuous shot, no text, no brand.”

### Shot 3 — The watch locks on (0:06–0:09)
**Prompt:** “A real human forearm in a dark tailored sleeve enters frame. The exact same assembled unbranded watch rotates gently and fastens around the wrist through elegant articulated metal segments. Show a believable clasp closure and natural wrist micro-movement. Camera tracks sideways with the wrist, then settles on the dial. Preserve the watch's case geometry, strap, hands and markers. Cinematic realism, clean anatomy, crisp detail, no text, no logo, no visible franchise costume.”

### Shot 4 — Original mechanical transformation (0:09–0:13)
**Prompt:** “The person stands in a dramatic hangar-like space overlooking the sky. Subtle precision-machined metallic panels extend from the wristwatch and interlock around the forearm and shoulder into an original, minimalist mechanical flight exosuit. This must be a new generic design, not any known superhero or film costume. Show panels moving in discrete mechanical stages, articulated hinges, servo movement and realistic contact shadows. Camera makes a steady low-angle push-in, controlled practical sparks only at a single metal lock, premium grounded sci-fi, no logos, no text.”

### Shot 5 — Flight moment (0:13–0:17)
**Prompt:** “Wide vertical cinematic shot of the same person, wearing the original graphite-and-champagne mechanical flight exosuit, standing at the open side of a high-altitude aircraft doorway above a sea of clouds. The person makes one decisive leap outward; the camera follows smoothly into open sky. Fabric and cloud wisps react naturally to airflow; the body orientation remains physically plausible. Dramatic but believable scale, smooth motion, realistic cloud parallax, no explosion, no franchise costume, no text or logo.”

### Shot 6 — Hero reveal (0:17–0:20)
**Prompt:** “Return to a clean premium dark studio. The exact same fictional watch floats upright and turns slowly by a few degrees, then comes to rest at a three-quarter angle. A narrow champagne light sweeps across the bezel and crystal; the second hand moves subtly. Camera does a short smooth push-in, leaving uncluttered negative space in the upper third for the editor to add a headline and lower safe zone for the CTA. Sharp product edges, detailed dial, restrained reflections, black graphite background, no generated words, no logo.”

## Universal negative prompt / rejection conditions

Where supported, add: “blurry product, changing watch design, duplicated watch, malformed dial, melting metal, random gears, extra fingers, broken anatomy, flicker, jitter, sudden zoom, unstable camera, low-resolution texture, fake text, watermarks added by the model, logos, famous characters, copied franchise armor, overexposed highlights, crushed black detail, oversharpened edges.”

Reject clips with any of these:
1. Watch geometry or strap changes between frames.
2. Dial/hand detail visibly melts or duplicates.
3. Motion is merely a still frame with zoom/pan.
4. Unmotivated shaking, flicker, morphing, or discontinuous body mechanics.
5. Unreadable or hallucinated text/logos.
6. Visible watermark inconsistent with the intended placement or rights.
7. Output rights or source-image permission cannot be verified for intended use.

## Tool eligibility gate (must be checked at time of use)

Do not hard-code old credit claims. Before spending a generation:
1. Sign in only to a service the operator already has access to; do not create paid subscriptions or accept a purchase prompt.
2. Verify that image-to-video or text-to-video is available to this account and region.
3. Record the exact model, duration, resolution, credit cost, and whether export can be downloaded.
4. Read the current terms for commercial use, watermarks, uploaded references, and client work.
5. Generate one 3–5 second motion test first; do not spend credits generating all six shots before quality is proven.
6. If a free route is personal/non-commercial only, do not use that output as a paid-client deliverable. Use it only for permitted internal experimentation, or find a route whose terms allow the intended commercial purpose.
7. If access requires payment, stop and report the blocker; never upgrade without explicit user approval.

### Known research caveats (checked 2026-10-28)

- Google Flow's current Help page says users generally need to be 18+, in a supported region, and subscribed to Google AI Plus/Pro/Ultra; qualifying Workspace users are an exception. It also says a visible watermark is automatically applied in India, South Korea, and Vietnam except on Google AI Ultra 20x. Therefore Flow is not treated as a confirmed ₹0 / watermark-free delivery route.
- Dreamina Help says free access, credits, feature access, and commercial eligibility depend on the account/feature/terms. Dreamina's current general Terms describe the service as generally for private, non-commercial use and may have feature-specific additional terms. Therefore do not deliver Dreamina output to a paying client until applicable commercial terms for the exact output are confirmed.
- A web result or marketing claim is not proof that a user's logged-in account can generate a clip. Verify the account UI and downloaded file.

## Assembly workflow after clips pass

1. Generate shots individually at the best free settings whose rights permit the intended use.
2. Download originals and record tool/model/settings/rights notes in a local evidence manifest.
3. Trim to the strongest 2.5–4 seconds per shot; maintain movement across cuts.
4. Assemble to a 9:16 / 1080 × 1920 timeline at 24 or 30 fps, without stretching low-resolution footage.
5. Add sound design (gear clicks, controlled servo lock, wind), only from licensed/free-to-use sources. Do not use a famous film score or unlicensed music.
6. Add exact copy in an editor after footage generation: one short headline, optional benefit, and a clearly readable closing CTA. Avoid claims about durability, water resistance, materials, or performance unless verified.
7. Check full playback and a frame-by-frame sample; inspect at normal phone size and 200% zoom.
8. Export MP4, H.264, vertical, and verify file duration, dimensions, audio, text margins, and playback before calling it complete.

## Human review checklist

- [ ] Six actual moving clips exist as downloaded files.
- [ ] All clips refer to the same fictional watch design.
- [ ] Motion is visible beyond camera-only motion.
- [ ] No frame flicker, geometry drift, malformed dial, or anatomical defects.
- [ ] Brand, CTA and any claims were added and checked after generation.
- [ ] Audio/source licenses and commercial terms are documented.
- [ ] Watermark policy is acceptable.
- [ ] Final exported MP4 is fully played back and visually checked.
- [ ] Evidence manifest records source files, generation settings, review outcome and export checksum.
- [ ] If any box is unchecked, mark the artifact **draft / blocked**, not finished.

## Reusable product-ad workflow for local businesses

After the watch benchmark passes, reuse the same pipeline but swap the product-specific shot plan:
- Salon: tool/product macro → process detail → customer experience (with consent) → result → booking CTA.
- Auto-parts: part macro → correct fitment context → detail/finish → workshop scene → verified availability/contact CTA.
- Cafe: pour/steam → food texture → environment → serving moment → visit/order CTA.

The workflow must change its prompts and checks per category; do not blindly reuse watch physics or fictional transformation scenes for real client products.

## Current completion state

- This file is a documented specification and prompt pack.
- No real motion clip, assembled final MP4, commercial rights review, client delivery, post publication, or payment is proven by this document.
