"""Device-adaptive task routing and safe agent-spec drafting (stdlib only).

This module recommends a route from declared, consented device capabilities. It
does not probe devices, install models, call remote APIs, or execute generated agents.
"""
from __future__ import annotations
import re
from typing import Any

from agents.device_adaptive_router import recommend_profile

ROUTER_VERSION = "0.2.0"


def classify_task(task: str) -> str:
    text = task.casefold()
    if any(w in text for w in ("transcribe", "speech to text", "audio transcription")):
        return "audio"
    if any(w in text for w in ("image", "photo", "vision", "video understanding")):
        return "vision"
    if any(w in text for w in ("debug", "write code", "refactor", "programming", "code review")):
        return "coding"
    if any(w in text for w in ("reason", "compare options", "plan a strategy", "multi-step", "deep analysis")):
        return "reasoning"
    if any(w in text for w in ("summarize", "summary", "translate", "classify text", "extract entities", "draft", "rewrite", "caption")):
        return "text"
    return "general"


def recommend_agent_profile(
    task_type: str,
    device: dict[str, Any] | None = None,
    installed_profiles: set[str] | None = None,
    allow_remote: bool = False,
) -> dict[str, Any]:
    """Bridge the agent factory to the versioned model-profile router.

    Only caller-confirmed, installed and smoke-tested profile IDs should be
    supplied in installed_profiles. This function recommends; it never executes.
    """
    result = recommend_profile(
        task_type=task_type,
        device=device,
        available_profiles=installed_profiles,
        allow_remote=allow_remote,
    )
    return {
        **result,
        "factory_version": ROUTER_VERSION,
        "execution_performed": False,
        "remote_called": False,
    }


def _nonnegative_number(device: dict[str, Any], key: str) -> float:
    value = device.get(key, 0)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{key} must be a non-negative number")
    return float(value)


def recommend_execution(task: str, device: dict[str, Any], allow_remote: bool = False) -> dict[str, Any]:
    """Return a recommendation only; no model or agent is executed by this function.

    Device fields are explicitly supplied by the caller after consent:
    free_ram_gb, free_vram_gb, local_runtime_available, internet_available.
    """
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task must be a non-empty string")
    if not isinstance(device, dict):
        raise ValueError("device must be a dictionary of declared capabilities")
    ram = _nonnegative_number(device, "free_ram_gb")
    vram = _nonnegative_number(device, "free_vram_gb")
    runtime = device.get("local_runtime_available", False) is True
    internet = device.get("internet_available", False) is True
    category = classify_task(task)
    base = {"router_version": ROUTER_VERSION, "task_category": category,
            "device_profile_source": "caller_declared_after_consent",
            "execution_performed": False, "remote_used": False}
    if category == "general" and any(w in task.casefold() for w in ("calculate", "validate json", "sort list", "parse csv")):
        return {**base, "route": "deterministic_local", "status": "recommended",
                "reason": "A deterministic local function is preferred for this task."}
    if category in {"audio", "vision"}:
        required = "audio" if category == "audio" else "vision"
        return {**base, "route": "specialist_model_required", "status": "blocked_unconfigured",
                "reason": f"No verified {required} model/runtime is configured by this router; do not assume capability."}
    if category in {"text", "coding", "reasoning", "general"} and runtime:
        if ram >= 12 or vram >= 8:
            profile = "local_model_medium_candidate"
            reason = "Declared memory suggests a medium local-model profile may fit; benchmark before adoption."
        elif ram >= 4 or vram >= 4:
            profile = "local_model_small_candidate"
            reason = "Declared memory may fit a small/quantized local model; benchmark before adoption."
        else:
            profile = None
            reason = "Declared free memory is below the router minimum for its local model candidates."
        if profile:
            return {**base, "route": profile, "status": "candidate_not_verified", "reason": reason,
                    "requires_checks": ["model weights available", "license reviewed", "memory benchmark", "task quality test"]}
    if allow_remote and internet:
        return {**base, "route": "remote_provider_candidate", "status": "approval_and_configuration_required",
                "reason": "Remote inference is not called; explicit provider configuration, privacy review, and cost approval are required."}
    return {**base, "route": "deterministic_or_manual_fallback", "status": "needs_local_runtime_or_review",
            "reason": "No verified local model route is available. Use a deterministic handler, install/configure a compatible local runtime manually, or return for review."}


def draft_agent_spec(name: str, purpose: str, capabilities: list[str],
                     allowed_tools: list[str] | None = None) -> dict[str, Any]:
    """Create a reviewable JSON-like agent specification; never executable code."""
    clean_name = re.sub(r"[^a-z0-9-]+", "-", str(name).strip().casefold()).strip("-")
    if not clean_name or not isinstance(purpose, str) or not purpose.strip():
        raise ValueError("name and purpose are required")
    if not isinstance(capabilities, list) or not capabilities or any(not isinstance(c, str) or not c.strip() for c in capabilities):
        raise ValueError("capabilities must be a non-empty list of non-empty strings")
    tools = allowed_tools or []
    if any(t not in {"local_files_read", "local_files_write_draft", "python_sandbox", "public_read_only"} for t in tools):
        raise ValueError("unknown tool permission; only the explicit safe allowlist is accepted")
    return {
        "agent_id": f"draft-{clean_name}",
        "agent_version": "0.1.0",
        "status": "draft_requires_evaluation",
        "name": clean_name,
        "purpose": purpose.strip()[:500],
        "capabilities": sorted(set(c.strip() for c in capabilities)),
        "allowed_tools": sorted(set(tools)),
        "model_profile": "selected_at_runtime_by_device_router",
        "permissions": {"public_publish": False, "send_message": False, "payments": False, "account_changes": False},
        "tests_required": ["input_schema", "expected_output", "quality_threshold", "privacy", "prompt_injection", "permission_boundary"],
        "release_gate": "human_review_after_tests",
        "execution_performed": False,
    }
