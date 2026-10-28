"""OpenAI-compatible LLM adapter for AutoPilot Studio.

Defaults to a local Ollama endpoint. Remote APIs are opt-in, require an explicit
base URL, and never fall back to paid billing automatically. This module returns
model text only; it does not execute tool calls or external actions.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_LOCAL_BASE_URL = "http://127.0.0.1:11434/v1"
DEFAULT_LOCAL_MODEL = "qwen3:4b"
DEFAULT_TIMEOUT_SECONDS = 45


class LLMConfigurationError(RuntimeError):
    """The selected inference backend is not configured safely."""


class LLMRequestError(RuntimeError):
    """The inference backend did not return a valid completion."""


@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    model: str
    api_key: str | None
    timeout_seconds: int
    remote: bool


def load_llm_config(environ: dict[str, str] | None = None) -> LLMConfig:
    env = os.environ if environ is None else environ
    base_url = env.get("AUTOPILOT_LLM_BASE_URL", DEFAULT_LOCAL_BASE_URL).strip().rstrip("/")
    model = env.get("AUTOPILOT_LLM_MODEL", DEFAULT_LOCAL_MODEL).strip()
    api_key = env.get("AUTOPILOT_LLM_API_KEY", "").strip() or None
    try:
        timeout = int(env.get("AUTOPILOT_LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    except ValueError as exc:
        raise LLMConfigurationError("AUTOPILOT_LLM_TIMEOUT_SECONDS must be an integer") from exc
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        raise LLMConfigurationError("LLM base URL must use HTTP(S)")
    if not model:
        raise LLMConfigurationError("AUTOPILOT_LLM_MODEL cannot be empty")
    if timeout < 1 or timeout > 180:
        raise LLMConfigurationError("timeout must be between 1 and 180 seconds")
    remote = not (base_url.startswith("http://127.0.0.1") or base_url.startswith("http://localhost"))
    if remote and env.get("AUTOPILOT_ALLOW_REMOTE_LLM", "").lower() != "true":
        raise LLMConfigurationError(
            "Remote inference is disabled by default. Set AUTOPILOT_ALLOW_REMOTE_LLM=true "
            "after reviewing the provider's free quota and privacy terms."
        )
    if remote and not api_key:
        raise LLMConfigurationError("Remote inference requires AUTOPILOT_LLM_API_KEY from an environment secret")
    return LLMConfig(base_url, model, api_key, timeout, remote)


def chat_completion(
    messages: list[dict[str, str]],
    *,
    config: LLMConfig | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1200,
) -> dict[str, Any]:
    """Call a local Ollama or explicitly enabled OpenAI-compatible endpoint."""
    cfg = config or load_llm_config()
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list")
    for item in messages:
        if not isinstance(item, dict) or item.get("role") not in {"system", "user", "assistant"}:
            raise ValueError("each message must have a supported role and content")
        if not isinstance(item.get("content"), str):
            raise ValueError("message content must be text")
    if not 0 <= temperature <= 2:
        raise ValueError("temperature must be between 0 and 2")
    if not 1 <= max_tokens <= 8192:
        raise ValueError("max_tokens must be between 1 and 8192")

    body = json.dumps({
        "model": cfg.model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if cfg.api_key:
        headers["Authorization"] = f"Bearer {cfg.api_key}"
    request = Request(f"{cfg.base_url}/chat/completions", data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=cfg.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        # Do not include request headers or secrets in the error message.
        raise LLMRequestError(f"LLM provider returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError) as exc:
        raise LLMRequestError(f"LLM provider unavailable: {type(exc).__name__}") from None
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise LLMRequestError("LLM provider returned invalid JSON") from None
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise LLMRequestError("LLM response missing choices[0].message.content") from None
    if not isinstance(text, str) or not text.strip():
        raise LLMRequestError("LLM response content was empty")
    usage = data.get("usage")
    return {
        "status": "completed",
        "model": cfg.model,
        "provider_mode": "remote_api" if cfg.remote else "local_endpoint",
        "content": text,
        "usage": usage if isinstance(usage, dict) else None,
        "tool_execution": "not_performed",
        "external_actions_performed": False,
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", default="You are AutoPilot Studio's careful assistant. Do not invent evidence.")
    parser.add_argument("--prompt", required=True)
    args = parser.parse_args()
    try:
        result = chat_completion([
            {"role": "system", "content": args.system},
            {"role": "user", "content": args.prompt},
        ])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (LLMConfigurationError, LLMRequestError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
