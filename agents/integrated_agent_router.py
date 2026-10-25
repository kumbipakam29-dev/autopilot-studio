"""Bridge the draft-agent factory to the versioned device-aware profile catalog.

This produces a reviewable package only. It never installs weights, executes agents,
sends messages, publishes content, or calls a remote model provider.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.adaptive_factory import classify_task, draft_agent_spec
from agents.device_adaptive_router import DEFAULT_CATALOG, recommend_profile


def _profile_task(task: str) -> str:
    text = task.casefold()
    category = classify_task(task)
    if any(word in text for word in ("validate json", "parse csv", "sort list", "calculate", "structured data")):
        return "validation" if "validat" in text else "structured"
    if any(word in text for word in ("deduplicate", "deduplication", "remove duplicates")):
        return "deduplication"
    if any(word in text for word in ("semantic search", "retrieve documents", "retrieval")):
        return "semantic_search" if "search" in text else "retrieval"
    if category == "coding":
        return "coding"
    if category == "reasoning":
        return "reasoning"
    if category == "audio":
        return "audio_transcription"
    if category == "vision":
        return "vision"
    if any(word in text for word in ("translate", "translation", "multilingual")):
        return "language"
    if any(word in text for word in ("classify text", "classification", "sentiment")):
        return "simple_classification"
    if any(word in text for word in ("draft", "caption", "rewrite", "write a post")):
        return "drafting"
    if category == "text":
        return "summarization"
    return "unsupported_task"


def build_agent_package(
    name: str,
    purpose: str,
    capabilities: list[str],
    task: str,
    device: dict[str, Any] | None = None,
    available_profiles: set[str] | None = None,
    allowed_tools: list[str] | None = None,
    allow_remote: bool = False,
    catalog_path: Path = DEFAULT_CATALOG,
) -> dict[str, Any]:
    """Create a versioned agent draft and model-route recommendation."""
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task must be a non-empty string")
    spec = draft_agent_spec(name, purpose, capabilities, allowed_tools)
    profile_task = _profile_task(task)
    # Avoid truthiness coercion: invalid falsy inputs such as [] must fail validation.
    route = recommend_profile(
        profile_task,
        device={} if device is None else device,
        available_profiles=available_profiles,
        catalog_path=catalog_path,
        allow_remote=allow_remote,
    )
    ready = route.get("route_status") == "ready"
    return {
        "package_schema_version": "1.0.0",
        "package_status": "draft_ready_for_human_review" if ready else "draft_blocked_on_model_setup_or_task_support",
        "agent_spec": spec,
        "model_route": route,
        "execution_performed": False,
        "external_actions_performed": False,
        "release_gate": "tests_and_human_review_required",
    }
