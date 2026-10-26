"""Free-first, device-aware model profile selection.

This module recommends a profile; it does not probe hardware, install weights,
start a model server, or claim inference is connected. Callers must obtain device
details with user consent and pass profiles that have actually been verified.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "agents" / "model_profiles.json"
DEFAULT_AVAILABLE = {"rules-engine"}


def load_profiles(path: Path = DEFAULT_CATALOG) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(catalog, dict):
        raise ValueError("Profile catalog root must be a JSON object")
    profiles = catalog.get("profiles", [])
    if not isinstance(profiles, list):
        raise ValueError("Profile catalog 'profiles' must be a list")
    if any(not isinstance(profile, dict) for profile in profiles):
        raise ValueError("Every model profile must be a JSON object")
    for profile in profiles:
        profile_id = profile.get("id")
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise ValueError("Profile IDs must be non-empty strings")
    ids = [profile["id"] for profile in profiles]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate model profile IDs")
    required = {"id", "version", "kind", "tasks", "min_ram_gb", "min_vram_gb"}
    for profile in profiles:
        missing = required - profile.keys()
        if missing:
            raise ValueError(f"Profile {profile.get('id')} missing {sorted(missing)}")
        for key in ("id", "version", "kind"):
            if not isinstance(profile[key], str) or not profile[key].strip():
                raise ValueError(f"Profile {profile.get('id')} {key} must be a non-empty string")
        if not isinstance(profile["tasks"], list) or any(not isinstance(t, str) or not t.strip() for t in profile["tasks"]):
            raise ValueError(f"Profile {profile['id']} tasks must be non-empty strings")
        for key in ("min_ram_gb", "min_vram_gb"):
            value = profile[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Profile {profile['id']} {key} must be a finite non-negative number")
    return catalog


def _device_supports(profile: dict[str, Any], device: dict[str, Any]) -> tuple[bool, str]:
    ram = device.get("ram_gb")
    vram = device.get("vram_gb")
    if isinstance(ram, bool) or (ram is not None and (not isinstance(ram, (int, float)) or not math.isfinite(ram) or ram < 0)):
        return False, "device RAM must be a finite non-negative number"
    if ram is None:
        if profile.get("min_ram_gb", 0) > 0:
            return False, "device RAM is unknown"
    elif ram < profile.get("min_ram_gb", 0):
        return False, f"requires about {profile['min_ram_gb']} GB RAM; reported {ram} GB"

    minimum_vram = profile.get("min_vram_gb", 0)
    if isinstance(vram, bool) or (vram is not None and (not isinstance(vram, (int, float)) or not math.isfinite(vram) or vram < 0)):
        return False, "device VRAM must be a finite non-negative number"
    if minimum_vram > 0:
        if vram is None:
            return False, "device VRAM is unknown"
        if vram < minimum_vram:
            return False, f"requires about {minimum_vram} GB VRAM; reported {vram} GB"
    return True, "device profile meets initial heuristic thresholds"


def recommend_profile(
    task_type: str,
    device: dict[str, Any] | None = None,
    available_profiles: set[str] | None = None,
    catalog_path: Path = DEFAULT_CATALOG,
    allow_remote: bool = False,
) -> dict[str, Any]:
    """Recommend the lowest-cost compatible profile without implying execution.

    available_profiles must contain only profiles whose runtime/model are
    genuinely installed and smoke-tested. Remote routing is disabled by default.
    """
    normalized_task = str(task_type or "").strip().lower()
    if device is not None and not isinstance(device, dict):
        raise ValueError("device must be a dictionary of declared capabilities")
    device_info = {} if device is None else device
    available = set(DEFAULT_AVAILABLE if available_profiles is None else available_profiles)
    catalog = load_profiles(catalog_path)
    candidates = [p for p in catalog["profiles"] if normalized_task in p.get("tasks", [])]
    if not candidates:
        return {
            "task_type": normalized_task,
            "route_status": "unsupported",
            "selected_profile": None,
            "execution_ready": False,
            "reason": "No catalog profile declares this task type.",
        }

    candidates.sort(key=lambda p: (p["kind"] != "deterministic", p.get("min_ram_gb", 0), p["id"]))
    compatible: list[tuple[dict[str, Any], str]] = []
    for profile in candidates:
        supported, reason = _device_supports(profile, device_info)
        if supported:
            compatible.append((profile, reason))
    if not compatible:
        return {
            "task_type": normalized_task,
            "route_status": "device_incompatible_or_unknown",
            "selected_profile": None,
            "execution_ready": False,
            "reason": "No candidate passed the initial device thresholds. Provide consented device capability details or use a smaller/different task.",
        }

    for profile, reason in compatible:
        if profile["id"] in available:
            return {
                "task_type": normalized_task,
                "route_status": "ready",
                "selected_profile": profile["id"],
                "profile_version": profile["version"],
                "execution_ready": True,
                "reason": reason,
                "remote_used": False,
            }

    profile, reason = compatible[0]
    return {
        "task_type": normalized_task,
        "route_status": "setup_required",
        "selected_profile": profile["id"],
        "profile_version": profile["version"],
        "execution_ready": False,
        "reason": "Compatible profile is only a catalog candidate; runtime and model installation/smoke test are not verified. " + reason,
        "remote_used": False,
        "remote_fallback_allowed": bool(allow_remote),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recommend a free-first model profile; no model is executed.")
    parser.add_argument("--task", required=True, choices=["structured", "formatting", "validation", "simple_classification", "language", "summarization", "drafting", "simple_reasoning", "reasoning", "coding", "semantic_search", "deduplication", "retrieval"])
    parser.add_argument("--ram-gb", type=float, default=None)
    parser.add_argument("--vram-gb", type=float, default=None)
    parser.add_argument("--available", action="append", default=[], help="Profile ID confirmed installed and smoke-tested; repeatable.")
    args = parser.parse_args()
    device = {}
    if args.ram_gb is not None:
        device["ram_gb"] = args.ram_gb
    if args.vram_gb is not None:
        device["vram_gb"] = args.vram_gb
    result = recommend_profile(args.task, device, set(args.available) | {"rules-engine"})
    print(json.dumps(result, indent=2))
