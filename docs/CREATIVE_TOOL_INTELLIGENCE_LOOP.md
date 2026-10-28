# Creative Tool Intelligence and Reverse-Engineering Loop

AutoPilot's goal is to learn from publicly observable creative workflows and build its own original implementation—not to clone proprietary internals or treat a vendor's marketing claims as benchmark results.

## Layers

1. **Tool intelligence registry** — source URL, capability, access model, cost caveat, license caveat and the part we can independently implement.
2. **Public-behaviour observation** — record an official demo/documentation page, date, visible inputs/outputs, unknowns and evidence scope.
3. **Hypothesis and original implementation** — e.g. reference-photo anchoring, separate camera and subject motion, editable post-production typography, shot-specific prompts, deterministic seeds, continuity checks.
4. **Controlled benchmark** — keep a fixed brief and compare the baseline and candidate on brief fit, concept diversity, product identity, temporal consistency, factuality, legibility and export quality.
5. **Human review and iteration** — only promote an improved candidate to review if every hard gate passes. Otherwise record the failed dimension, change one or two variables, and run the same suite again.
6. **No automatic release** — the loop never silently deploys, publishes, copies private code, bypasses access controls or selects a paid model.

## Commands

List the source-linked tool registry:

```bash
python -m agents.creative_tool_intelligence --list-tools
```

Recommend a shortlist for a zero-budget, local-first cinematic Reel:

```bash
python -m agents.creative_tool_intelligence --task premium_cinematic_reel
```

Other tasks: `image_to_video`, `text_heavy_poster`, `storyboard`, `video_quality_review`, `brand_consistency`, `video_edit_export`.

Turn a public observation into original, testable engineering hypotheses:

```bash
python -m agents.creative_tool_intelligence --observation examples/creative-tool-observation-pika.json
```

CI runs this analysis for source-linked public observations about Pika keyframes, Adobe multi-step creative workflows, VBench quality dimensions, ComfyUI workflow graphs and Ideogram typography.

Run an evidence-and-benchmark cycle:

```bash
python -m agents.creative_tool_intelligence --cycle examples/creative-reverse-engineering-cycle.json --ledger artifacts/creative-tool-intelligence/learning-ledger.jsonl
python -m agents.creative_tool_intelligence --history --ledger artifacts/creative-tool-intelligence/learning-ledger.jsonl
```

The JSONL ledger deduplicates cycle IDs, records metric provenance and excludes placeholder/unmeasured scores from the best-candidate comparison. Reuse the same local ledger path to persist cycles across runs; a fresh CI run creates a fresh artifact snapshot unless a prior ledger is deliberately restored.

All metric scores must be supplied from actual output reviews or a documented evaluator, on a 0–5 scale. The program does not fabricate measurements. A score increase without rights, factuality, privacy, originality and actual-output gates cannot promote a candidate. A passed score recommends human review, not automatic production deployment.

## Source-linked market observations (checked 28 October 2026)

- **ComfyUI** provides a local node-graph workflow, reusable subgraphs, an API and support for image/video/audio/3D models; custom nodes and model licenses must be checked separately. Source: https://github.com/Comfy-Org/ComfyUI and https://github.com/Comfy-Org/docs/blob/main/development/api-development/workflow-api-format.mdx
- **Wan2.2** publishes model weights and inference code under Apache 2.0 according to its repository. This does not remove hardware and dependency requirements. Source: https://github.com/Wan-Video/Wan2.2
- **LTX-2.5** uses a version-specific LTX community license, not an unconditional Apache/MIT grant. Re-check the exact version and commercial eligibility. Source: https://github.com/Lightricks/LTX-2 and https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x
- **VBench** evaluates video quality across dimensions including subject/background consistency, temporal flicker, motion smoothness, aesthetics and image quality. AutoPilot's first-pass rubric is inspired by those dimensions; it is not a substitute for the benchmark. Source: https://github.com/Vchitect/VBench
- **Pika** documents photo animation and transitions between ordered keyframes; plan tiers, credits and watermark terms can vary. Source: https://creation.pika.art/apps/pikaframes?tab=video-tools and https://pika.art/faq
- **Ideogram** focuses on text rendering in images. Its accuracy number is a vendor claim; AutoPilot should still proofread every offer, price, date and CTA. Source: https://ideogram.ai/features/text-rendering/
- **Krea** presents a multi-model workflow for image/video generation, editing, enhancement and style references. Hosted access is not the same as a free local model. Source: https://www.krea.ai/
- **Canva Magic Video** documents turning photos/clips into template-guided edits; automation can save time but may look generic if the creative concept is not customized. Feature availability varies by plan and locale. Source: https://www.canva.com/help/magic-video/
- **Adobe Firefly Creative Agent** describes brand kits, storyboards-to-video, product-photo video and quick-cut workflows. AutoPilot can independently implement the broad stages without attempting to copy private internals. Source: https://news.adobe.com/news/2026/06/adobe-unveils-major-expansion
- **Runway Workflows** documents chaining multiple model and editing steps into reusable workflows, and describes model routing across quality/cost/latency trade-offs. It is an architectural reference, not assumed free infrastructure. Source: https://dev.runwayml.com/workflows and https://dev.runwayml.com/learn/generate-product-videos
- **FFmpeg** provides local media filtering, transcoding and export controls; check the specific build and its licensing before redistribution. Source: https://www.ffmpeg.org/ffmpeg.html
- **Pillow** provides local pixel-level image composition and drawing APIs, useful for exact text overlays added after image generation. Source: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
- **OpenCV** provides local computer-vision and frame processing operations that can help detect blur, crop changes and frame differences. Source: https://github.com/opencv/opencv
- **Whisper** publishes speech-recognition code and model weights under MIT according to its repository, useful for subtitle drafts that still require proofreading. Source: https://github.com/openai/whisper

## Useful AutoPilot differentiators to benchmark

- Three structurally different story routes, not the same template with changed colours.
- Product/brand identity preserved across frames and shots.
- Mechanical parts follow plausible trajectories rather than arbitrary explosions.
- Salon/hair motion does not distort faces, skin or hair identity.
- Store walkthrough preserves shelf geometry and product packaging.
- Typography added as editable post-production layers and checked at phone size.
- Shot lengths, safe zones, resolution, FPS, audio loudness and codec verified from actual exports.
- Cost, model license, asset rights, consent and source provenance recorded per run.
- Learning only from confirmed client feedback and actual analytics; never claim that a model score proves sales or virality.

## Important boundary

This is an evidence-led research and experiment framework. It currently analyzes supplied, source-linked public observations; it does not automatically browse for new tools, inspect paid-tool internals, generate model weights, run real media benchmarks, or prove that a candidate is superior until real outputs and documented measurements have been reviewed.
