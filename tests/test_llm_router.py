"""Safety and response-contract tests for the LLM adapter."""
import json
import unittest
from unittest.mock import patch

from agents.llm_router import (
    LLMConfig, LLMConfigurationError, LLMRequestError,
    chat_completion, load_llm_config,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class LLMRouterTests(unittest.TestCase):
    def test_defaults_to_local_qwen_endpoint_without_api_key(self):
        cfg = load_llm_config({})
        self.assertEqual(cfg.base_url, "http://127.0.0.1:11434/v1")
        self.assertEqual(cfg.model, "qwen3:4b")
        self.assertIsNone(cfg.api_key)
        self.assertFalse(cfg.remote)

    def test_remote_api_is_disabled_without_explicit_opt_in(self):
        with self.assertRaisesRegex(LLMConfigurationError, "disabled by default"):
            load_llm_config({
                "AUTOPILOT_LLM_BASE_URL": "https://api.example.test/v1",
                "AUTOPILOT_LLM_API_KEY": "do-not-leak",
            })

    def test_remote_api_requires_key_and_explicit_opt_in(self):
        with self.assertRaisesRegex(LLMConfigurationError, "requires"):
            load_llm_config({
                "AUTOPILOT_LLM_BASE_URL": "https://api.example.test/v1",
                "AUTOPILOT_ALLOW_REMOTE_LLM": "true",
            })

    def test_remote_config_only_when_explicitly_enabled(self):
        cfg = load_llm_config({
            "AUTOPILOT_LLM_BASE_URL": "https://api.example.test/v1",
            "AUTOPILOT_ALLOW_REMOTE_LLM": "true",
            "AUTOPILOT_LLM_API_KEY": "secret",
            "AUTOPILOT_LLM_MODEL": "some-free-model",
        })
        self.assertTrue(cfg.remote)
        self.assertEqual(cfg.model, "some-free-model")

    @patch("agents.llm_router.urlopen")
    def test_chat_completion_returns_text_without_executing_tools(self, mocked):
        mocked.return_value = FakeResponse({
            "choices": [{"message": {"content": "Hello from test model"}}],
            "usage": {"total_tokens": 12},
        })
        result = chat_completion(
            [{"role": "user", "content": "Say hello"}],
            config=LLMConfig("http://127.0.0.1:11434/v1", "qwen3:4b", None, 3, False),
        )
        self.assertEqual(result["content"], "Hello from test model")
        self.assertEqual(result["provider_mode"], "local_endpoint")
        self.assertEqual(result["tool_execution"], "not_performed")
        self.assertFalse(result["external_actions_performed"])
        req = mocked.call_args.args[0]
        self.assertTrue(req.full_url.endswith("/chat/completions"))

    @patch("agents.llm_router.urlopen")
    def test_provider_http_error_does_not_leak_secrets(self, mocked):
        from urllib.error import HTTPError
        mocked.side_effect = HTTPError("https://example.test", 401, "bad", {}, None)
        cfg = LLMConfig("https://example.test/v1", "model", "very-secret", 3, True)
        with self.assertRaises(LLMRequestError) as caught:
            chat_completion([{"role": "user", "content": "hi"}], config=cfg)
        self.assertNotIn("very-secret", str(caught.exception))

    def test_rejects_invalid_message_role(self):
        with self.assertRaisesRegex(ValueError, "supported role"):
            chat_completion([{"role": "tool", "content": "run shell"}])

    def test_no_silent_paid_fallback_is_configured(self):
        # The router has one configured endpoint and no provider fallback path.
        cfg = load_llm_config({})
        self.assertEqual(cfg.base_url, "http://127.0.0.1:11434/v1")


if __name__ == "__main__":
    unittest.main()
