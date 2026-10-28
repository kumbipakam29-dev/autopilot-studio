# ComfyUI Render Adapter

AutoPilot Studio can hand an approved, exported ComfyUI API workflow to a reachable ComfyUI server using the standard-library-only client in `agents/comfyui_render_client.py`.

## Workflow placeholders

In the ComfyUI API-format JSON, use these exact strings where values should be supplied at runtime:

- `__AUTOPILOT_POSITIVE_PROMPT__`
- `__AUTOPILOT_NEGATIVE_PROMPT__`
- `__AUTOPILOT_IMAGE_FILENAME__`
- `__AUTOPILOT_SEED__`
- `__AUTOPILOT_OUTPUT_PREFIX__`

The workflow must be exported in ComfyUI API format, where nodes are a dictionary containing `class_type` and `inputs`. UI-format workflows are not accepted.

## Check and run

Check that the local service responds without submitting a job:

```bash
python -m agents.comfyui_render_client --check
```

Execution requires the explicit `--execute` flag. Add `--wait` to wait for supported output files and download them:

```bash
python -m agents.comfyui_render_client --workflow workflow_api.json --image approved-client-photo.png --positive-prompt "Use the approved visual prompt" --negative-prompt "text, logo distortion, flicker" --seed 123 --execute --wait --output-dir artifacts/comfyui
```

Default endpoint is `http://127.0.0.1:8188`. Remote endpoints are blocked unless `AUTOPILOT_ALLOW_REMOTE_COMFYUI=true` is configured. Obvious third-party provider nodes are blocked unless `AUTOPILOT_COMFYUI_ALLOW_PROVIDER_NODES=true` is set after review.

## Zero-budget and safety caveats

- No model is downloaded or installed by this adapter, and no real render was executed by CI.
- Review the complete workflow and every custom node before execution; node-name checks cannot guarantee that every workflow is local or free of charges.
- Use a trusted local endpoint where possible. A remote ComfyUI endpoint may receive client photos and prompts; secure it appropriately.
- Hardware and model requirements depend on the selected workflow. A successful API submission is not proof of a completed render; output is only marked complete when output files are retrieved.
- Text, logos, product details, generated motion, rights and export quality still require review before customer delivery.
