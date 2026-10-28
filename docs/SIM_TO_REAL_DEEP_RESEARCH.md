# Deep Research: Building a Simulation-to-Reality Bridge
**AutoPilot Digital Studio | Research snapshot: 28 October 2026**  
**Use case:** cinematic product ads starting with a watch, then local-business ads.  
**Budget rule:** ₹0 first; free/open-source tools; no paid API, cloud upgrade or subscription without approval.

> **Status honesty:** this document is research and an engineering plan, not proof that a video has been rendered or that an output looks photorealistic. A pipeline is validated only after an actual MP4 is played and inspected.

## Executive finding

The most promising bridge is **real reference + structured 3D scene + deterministic simulation/rendering + controlled generative motion + evidence-based QA**. Do not rely on a text-to-video model to invent the whole commercial in one pass.

1. Anchor important visual facts to real product imagery/video, approved CAD or dimensions.
2. Represent scene, geometry, camera, lights, material parameters and motion as structured data.
3. Simulate/render motion that must be correct; preserve logos, mechanics and typography deterministically.
4. Use generative video only for bounded tasks—short keyframe animation, atmosphere or non-critical transitions.
5. Compare the result with reference frames and explicit acceptance checks; reject bad clips and correct the responsible layer.
6. Keep a CPU/3D fallback, so lack of free GPU access never forces spending.

This does not remove compute requirements for frontier AI video. It reduces dependence on a single large hosted model and allows useful, repeatable work without one.

## 1. What “sim-to-real” means here

**Creative-production sim-to-real:** create or reconstruct a controllable scene, render it under controlled camera/light/material conditions, and compare the result to real evidence. Goal: believable advertising visuals while preserving product identity.

**Physical-AI / robotics sim-to-real:** transfer behaviour from simulation to physical devices. The reality gap includes sensor noise, friction, contacts, deformation, material differences and calibration.

The fields share a lesson: simulation only helps when its assumptions are explicit and results are compared against observations. The robotics reality-gap survey discusses these issues and methods including domain randomization and real-to-sim: https://doi.org/10.1146/annurev-control-031924-100130

For AutoPilot, start with creative-production sim-to-real and borrow the engineering ideas—controlled variables, repeatable tests and feedback—not claims about real-world mechanical performance.

## 2. What the newest research says

### Physical simulator-in-the-loop video generation
The CVPR 2026 paper *Physical Simulator In-the-loop Video Generation* reconstructs a scene and foreground meshes from a template video, puts them in a physics simulator, computes more consistent trajectories, then guides the video generator using them. It directly targets drift and implausible motion:  
https://openaccess.thecvf.com/content/CVPR2026/html/Foo_Physical_Simulator_In-the-Loop_Video_Generation_CVPR_2026_paper.html

**Why this matters:** simulation and generative video are not competing alternatives. The promising design is a feedback loop: generate a controlled motion reference, animate/generate around it, compare the result, and retry or fall back to the render. Reproducing the full research system is not the first milestone; we can build a smaller approximation.

### Physical priors for generative motion
The CVPR 2026 paper *PhyCo* uses simulation clips with systematically varied physical properties such as friction, restitution and force, along with aligned property maps, to improve control of generated video:  
https://openaccess.thecvf.com/content/CVPR2026/html/Narayanan_PhyCo_Learning_Controllable_Physical_Priors_for_Generative_Motion_CVPR_2026_paper.html

**Transferable idea:** make key properties explicit. Keep dimensions, pivots, material class, camera path, timing and expected motion in the shot plan, rather than hiding everything inside a long prompt.

### New physical-plausibility benchmarks
PVBench, posted 19 October 2026, proposes assessment over 46 dimensions, including geometry, kinematics, materials and mechanical plausibility: https://arxiv.org/abs/2610.26711. This is a recent preprint, not evidence the problem is solved.

PAI-Bench (CVPR 2026) also reports that visually compelling generative video can still struggle with physically coherent dynamics:  
https://openaccess.thecvf.com/content/CVPR2026/html/Zhou_PAI-Bench_A_Comprehensive_Benchmark_For_Physical_AI_CVPR_2026_paper.html

VBench separates video quality into 16 dimensions, including subject/background consistency, flicker, motion smoothness and spatial relationships:  
https://openaccess.thecvf.com/content/CVPR2024/html/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.html

**Practical conclusion:** “HD” resolution is not a quality metric by itself. Identity drift, bad contact, wrong materials and flickering details can ruin a sharp clip.

## 3. Open tools and compute reality

| Tool/model | Strength | Constraint and intended use |
|---|---|---|
| Blender | Geometry, camera, lighting, materials, animation, render passes and compositing | Backbone. CPU rendering is possible but may be slow; GPU use depends on hardware support. |
| Wan2.2 TI2V-5B | Text/image-to-video at 720p | Official documented single-GPU path requires at least 24 GB VRAM. Candidate only if available free GPU fits. |
| Wan2.2 A14B | Larger generation model | Official repo says at least 80 GB VRAM for its documented single-GPU path; not our first zero-budget target. |
| LTX Desktop / LTX models | Keyframes, image/video workflows, open model ecosystem | Current official desktop requirements list 24 GB+ NVIDIA VRAM (32 GB recommended), 32 GB RAM and about 100 GB free disk for local use; confirm model/version requirements. |
| ComfyUI | Reusable node graphs for image/video workflows | Compute depends on the model. A workflow that invokes an online API may cost money; “ComfyUI” does not automatically mean free inference. |
| COLMAP | Camera/3D reconstruction from multiple photographs | Works best with adequate overlapping, textured views; not magic 3D recovery from a single photo. |
| FFmpeg | Clip trim, resize, FPS/pixel-format normalization, concat, audio mux and export checks | CPU-friendly finishing and reproducible delivery. |

Official sources:
- Wan2.2 inference and hardware notes: https://github.com/Wan-Video/Wan2.2
- LTX Desktop local requirements: https://github.com/Lightricks/LTX-Desktop
- Blender rendering manual: https://docs.blender.org/manual/en/4.5/render/introduction.html
- COLMAP documentation: https://colmap.github.io/
- NVIDIA controlled-video playbook: https://build.nvidia.com/playbooks/video-gen-guide/overview

NVIDIA's workflow explicitly uses scene assets, composition/depth-guided keyframes and first/last-frame generation rather than relying only on a text prompt. This supports the “layout first, generative video second” strategy.

Free hosted GPU capacity, quotas, model availability and session duration can change. Treat remote GPUs as optional workers, not permanent infrastructure. Store prompts, source assets, seeds, model/version, settings and intermediate renders so work can be resumed on another machine. **Do not pay just because a free runtime is busy.**

## 4. Architecture: the AutoPilot Sim-to-Reality Bridge

### Layer 0 — Evidence and asset truth
Every asset should state source, version, usage rights, dimensions/scale confidence, critical visible features and known unknowns. Source categories: real reference, approved CAD, reconstructed, synthetic/spec concept, unknown.

For client work, confirm brand asset rights and customer approval. Do not claim a fictional watch depicts a real model. Do not invent logos, testimonials, certifications, prices or product capabilities.

### Layer 1 — Structured scene description
Store the production plan as JSON/YAML data rather than prose only:
- objects, hierarchy, dimensions and pivots;
- camera position, focal length, target, path and focus;
- light size/position and reflection-card placement;
- material properties such as roughness, metallic and transmission;
- motion curve and shot timing;
- aspect ratio, frame rate, output dimensions;
- reference asset and shot-specific acceptance tests.

For a watch, build case, dial, hands, indices, crown, bezel and strap as distinct parts. Visible meshing gears need aligned axes and plausible motion. If the actual internal mechanism is unknown, call the shot a stylized abstract insert—not an accurate view of that watch's mechanism.

### Layer 2 — Deterministic simulation and render
Use Blender/Python to build or import geometry, validate silhouette with a neutral material pass, then set physically based materials, studio lighting and reflections. Animate objects using controlled transforms and constraints; make a low-resolution animatic first. After motion/composition approval, render final frames and useful passes such as beauty, depth, normals and object masks/IDs.

A cinematic look often depends more on shape, reflections, composition, lens/focus and timing than simply raising the pixel count.

### Layer 3 — Optional generative enhancement
Choose per shot:
- **A. Pure 3D/render:** best for exact product geometry, gears, logos, typography and repeatable motion.
- **B. Keyframe-conditioned image-to-video:** prepare a strong first frame and, when supported, an end frame. Keep the shot short and camera movement moderate.
- **C. Control-conditioned generation:** use depth, masks, pose or control adapters only when the chosen workflow actually supports them.
- **D. Atmosphere-only generation:** create a non-critical background/transition, then composite the real product render over it.
- **E. Real-footage composite:** for local businesses, real phone-shot products, staff, storefronts and demonstrations can be more trustworthy than replacing everything synthetically.

First/last frames anchor composition but do not guarantee every intermediate frame is correct. If the object warps, reduce motion, shorten/split the shot, or use the deterministic version.

### Layer 4 — Editorial finishing
Use a compositor/editor for colour, typography, logos, price and CTA; use FFmpeg for normalized assembly. Keep all small text as vector/text layers—not generated pixels. Check crop, safe areas, audio and actual readability on a phone. Avoid aggressive sharpening that creates halos; it cannot recover real geometry/detail that never existed.

### Layer 5 — Quality gates
Create a contact sheet and inspect frames through the whole clip. Automated checks should include:
- valid codec, dimensions, frame rate and audio;
- no black/frozen frames or broken exports;
- subject identity and component continuity;
- no unexplained drift or impossible motion;
- plausible light/shadow/material response;
- crisp, stable text/logo at delivery size;
- human review at normal mobile playback scale.

A VLM can flag defects but should not be the sole authority for physical correctness or client approval.

## 5. First prototype: a controlled four-shot watch ad

This is a test concept, not a claim that the rendered watch is a real commercial product.

1. **Macro detail, 2–3 s:** bezel/dial/case, slow lateral move and a controlled highlight sweep. Use approved real reference or label as fictional design.
2. **Mechanism insert, 2–3 s:** approved internal CAD/reference, or a visibly stylized gear assembly. Do not invent mechanism-specific facts.
3. **Wrist/scale shot, 3–4 s:** safest is approved real wrist footage. Synthetic hands, skin contact and watch fit are failure-prone; keep the shot simple if generated.
4. **Hero reveal, 3–4 s:** controlled orbit/dolly, clean silhouette and designed reflections; add text separately.

Start with 10–14 seconds, not a 20-second single generation. Test each shot independently first. For one shot, compare three variants while changing only one variable at a time—camera speed, light size or conditioning—so defects can be diagnosed.

**Pass/fail gates**
- G0: reference, permissions and synthetic-vs-real status clear.
- G1: stable geometry; no surprise shape changes.
- G2: plausible motion; no drift or visibly impossible interaction.
- G3: credible materials and light.
- G4: details remain stable at native resolution.
- G5: typography/CTA is sharp and readable on a phone.
- G6: playable MP4, correct framing/FPS/audio, rights and human approval.

Any hard failure means reject or rework that layer. Do not use upscaling to hide major structural errors.

## 6. Reuse the pipeline for small businesses

| Client type | Real anchor | Simulate/render | Keep real or deterministic |
|---|---|---|---|
| Cafe/restaurant | Actual dishes, counter, staff, storefront | Camera movement, titles, menu graphics, transitions | Menu/ingredients, prices, offer terms, address |
| Salon | Actual salon and approved service footage | Intro/outro, typography, designed transitions | Before/after truth, results, consent |
| Auto-parts shop | Actual products, packaging and shelf | Turntable/product layout, documented exploded view | Part number, compatibility, brand, warranty |
| Local service | Actual team, tools and worksite | Motion graphics, paced cut plan, titles | Credentials, price, service area, testimonials, guarantees |

The scalable service is not “AI invents everything.” It is a repeatable production system that uses real client proof, controlled motion and premium finishing, with generative AI used only where it improves the result.

## 7. The feedback loop

1. **Plan:** shot data, reference evidence, claims and acceptance criteria.
2. **Build:** deterministic scene and low-resolution animatic.
3. **Render:** reference frames, and depth/masks if useful.
4. **Enhance:** optional short image-to-video or controlled-video run.
5. **Measure:** codec, black frames, sharpness/flicker proxies and object-mask drift when masks are available.
6. **Compare:** contact sheet against reference anchors; do not infer uncalibrated real-world scale.
7. **Diagnose:** classify failure as geometry, material/light, camera, generated temporal inconsistency, text, or encoding.
8. **Repair only the responsible layer:** bad highlights -> light/material; wrong silhouette -> geometry/reference; warped subject -> simpler/shorter shot or deterministic fallback.
9. **Human gate:** inspect on phone at native output size.
10. **Freeze:** save asset rights, model/version, seed/settings, source hashes, final MP4 and failure notes.

Initially, learning should mean a versioned defect/correction log, not a claim of automatic self-training. A new video-model training run is not required for the first milestone.

## 8. Zero-budget build plan

**Phase 1 — Deterministic baseline:** generate four simple Blender scenes, render low-res frames and assemble a valid MP4 with FFmpeg. Reject anything that still looks like a vector infographic rather than product footage.

**Phase 2 — Compute preflight:** record OS, CPU, RAM, free disk, GPU and VRAM. Check model licence/weights before downloading large files. Download one model only after identifying a compatible free runtime.

**Phase 3 — One short I2V experiment:** use one carefully authored 9:16 keyframe, modest duration and a fixed seed. Preserve settings and all frames; inspect every shot before scaling.

**Phase 4 — Compare routes:** for the same shot, compare (A) Blender-only, (B) Blender keyframe plus image-to-video, and (C) real footage plus compositing. Choose per shot based on visual trust, repair cost, runtime and repeatability.

**Phase 5 — Productize:** build client intake, shot templates, text overlays, QA report and delivery checklist. Ask customers for approved source footage and verify claims before publishing.

**Free-GPU stop rule:** if no free GPU is usable, keep progressing with CPU/Blender rendering and editorial work. Never buy credits to get past a quota or queue.

## 9. Risks to keep explicit

- A single photo cannot reveal unseen surfaces or exact dimensions.
- Shiny metal, glass and glossy black surfaces challenge photogrammetry because reflections move with the camera; manual/CAD geometry may be safer.
- Good first/last frames do not guarantee identity-consistent intermediate frames.
- A physics solver is not product-engineering validation.
- Model weights and code may have different licences; check commercial-use terms before client delivery.
- Free GPU availability, quotas and runtime limits are not guaranteed.
- Do not rely on one VLM score or a high-resolution screenshot; use human review at delivery size.
- Do not claim the ad is real footage if it is synthetic, or show invented details as product facts.

## 10. Repository next steps

1. Keep the Kaggle GPU notebook as an optional experiment, not the only workflow.
2. Add a Blender scene builder that can render on CPU.
3. Add example shot-plan and asset-manifest data.
4. Add FFmpeg validation and contact-sheet generation.
5. Require a one-frame/one-short-clip review before full multi-shot rendering.
6. Record actual runtime, peak RAM/VRAM, settings, output hash and pass/fail notes.
7. Say “rendered” only when a video file exists; say “validated” only after the actual file has been watched and inspected.

## Sources

- PSIVG, CVPR 2026: https://openaccess.thecvf.com/content/CVPR2026/html/Foo_Physical_Simulator_In-the-Loop_Video_Generation_CVPR_2026_paper.html
- PhyCo, CVPR 2026: https://openaccess.thecvf.com/content/CVPR2026/html/Narayanan_PhyCo_Learning_Controllable_Physical_Priors_for_Generative_Motion_CVPR_2026_paper.html
- PVBench preprint, 2026-10-19: https://arxiv.org/abs/2610.26711
- PAI-Bench, CVPR 2026: https://openaccess.thecvf.com/content/CVPR2026/html/Zhou_PAI-Bench_A_Comprehensive_Benchmark_For_Physical_AI_CVPR_2026_paper.html
- VBench, CVPR 2024: https://openaccess.thecvf.com/content/CVPR2024/html/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.html
- Wan2.2 official repo: https://github.com/Wan-Video/Wan2.2
- LTX Desktop requirements: https://github.com/Lightricks/LTX-Desktop
- NVIDIA controlled-video playbook: https://build.nvidia.com/playbooks/video-gen-guide/overview
- Blender manual: https://docs.blender.org/manual/en/4.5/render/introduction.html
- COLMAP documentation: https://colmap.github.io/
- Robotics reality-gap survey: https://doi.org/10.1146/annurev-control-031924-100130

---
**Bottom line:** build the bridge before betting on one large model. The first proof is a believable, inspectable MP4—not a prompt, notebook, repository commit or promise.
