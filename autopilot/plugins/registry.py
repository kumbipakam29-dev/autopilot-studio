"""Small dependency-free plugin registry for AutoPilot Studio."""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class Plugin:
    name: str
    version: str
    description: str
    handler: Callable[..., Any]
    health_check: Optional[Callable[[], bool]] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def status(self) -> str:
        if not self.enabled:
            return "disabled"
        if self.health_check is None:
            return "configured"
        try:
            return "connected" if self.health_check() else "not_connected"
        except Exception:
            return "error"


class PluginRegistry:
    """Register, inspect, and dispatch approved plugin handlers."""

    def __init__(self) -> None:
        self._plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        key = plugin.name.strip().lower()
        if not key:
            raise ValueError("Plugin name cannot be empty")
        if key in self._plugins:
            raise ValueError(f"Plugin already registered: {key}")
        self._plugins[key] = plugin

    def get(self, name: str) -> Plugin:
        try:
            return self._plugins[name.strip().lower()]
        except KeyError as exc:
            raise KeyError(f"Unknown plugin: {name}") from exc

    def list_plugins(self) -> list[dict[str, Any]]:
        return [
            {"name": p.name, "version": p.version, "description": p.description,
             "enabled": p.enabled, "status": p.status(), "metadata": dict(p.metadata)}
            for p in sorted(self._plugins.values(), key=lambda item: item.name)
        ]

    def dispatch(self, name: str, *, approved: bool = False, **payload: Any) -> Any:
        plugin = self.get(name)
        if not plugin.enabled:
            raise RuntimeError(f"Plugin is disabled: {name}")
        if not approved:
            raise PermissionError("Dispatch requires explicit approval")
        if plugin.status() in {"not_connected", "error"}:
            raise RuntimeError(f"Plugin is not healthy: {name}")
        return plugin.handler(**payload)
