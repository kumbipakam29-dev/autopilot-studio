# ComfyUI Render Adapter

AutoPilot Studio can hand an approved, exported ComfyUI API workflow to a reachable ComfyUI server using the standard-library-only client in `agents/comfyui_render_client.py`. The shot runner in `agents/cinematic_render_runner.py` queues all timed shots from one selected concept.

## Workflow placeholders

In the ComfyUI API-format JSON, use these exact strings where values should be supplied at runtime:

- `__AUTOPILOT_POSITIVE_PROMPT__`
- `__AUTOPILOT_NEGATIVE_PROMPT__`
- `__AUTOPILOT_IMAGE_FILENAME__`
- `__AUTOPILOT_SEED__`
- `__AUTOPILOT_OUTPUT_PREFIX__`

The workflow must be exported in ComfyUI API format, where nodes are a dictionary containing `class_type` and `inputs`. UI-format workflows are not accepted.

## Concept planning and render queue

Create three original creative routes and four shot prompts per route:

```bash
python -m agents.cinematic_ad_planner --brief client-brief.json --output artifacts/cinematic-ad-pack.json
```

Optional configured LLM drafting (defaults remain deterministic; there is no silent fallback if the LLM was explicitly requested):

```bash
python -m agents.cinematic_ad_planner --brief client-brief.json --use-llm --output artifacts/cinematic-ad-pack.json
```

Check that the local service responds without submitting a job:

```bash
python -m agents.comfyui_render_client --check
```

Submit four scenes for the selected concept and wait for output files:

```bash
python -m agents.cinematic_render_runner --pack artifacts/cinematic-ad-pack.json --workflow workflow_api.json --concept route_1 --execute --wait --output-dir artifacts/cinematic-renders
```

For an image-to-video workflow, add both `--image approved-client-photo.png` and `--asset-permission-confirmed`. The workflow must contain the matching image placeholder. The runner adds scene-specific visual and motion prompts to the positive prompt field. If `--wait` is omitted, jobs are submitted and reported as pending rather than falsely marked complete.

## Endpoint and execution guards

Default endpoint is `http://127.0.0.1:8188`. Remote endpoints are blocked unless `AUTOPILOT_ALLOW_REMOTE_COMFYUI=true` is configured. Obvious third-party provider nodes are blocked unless `AUTOPILOT_COMFYUI_ALLOW_PROVIDER_NODES=true` is set after review. `--execute` is required to submit jobs.

The API surface is based on ComfyUI's published endpoint definitions: [ComfyUI API schema](https://github.com/Comfy-Org/ComfyUI/blob/master/openapi.yaml). Exact node schemas depend on the installed ComfyUI version and custom nodes.

## Zero-budget and safety caveats

- The adapter does not download or install a model. CI tests use mocks; they do not prove that a live ComfyUI server or video model is installed.
- Review the complete workflow and every custom node before execution; node-name checks cannot guarantee that every workflow is local or free of charges.
- Use a trusted local endpoint where possible. A remote endpoint may receive client photos and prompts; secure it appropriately.
- Local video generation is hardware-dependent. For example, the [Wan2.2 project](https://github.com/Wan-Video/Wan2.2) documents 24 GB GPU memory for its 5B text-image-to-video path and 80 GB for its larger I2V-A14B path. The [LTX Desktop requirements](https://github.com/Lightricks/LTX-Desktop/) also describe demanding local hardware floors. These are model-specific examples, not universal ComfyUI requirements.
- A successful job submission is not proof of a completed render; output is only marked complete when output files are retrieved.
- Text, logos, product details, generated motion, rights and export quality still require review before customer delivery.
