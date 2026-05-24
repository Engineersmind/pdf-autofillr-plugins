"""
Built-in: LiteLLMAdapter

Production LLM adapter using LiteLLM — supports OpenAI, Anthropic,
Google Gemini, Ollama, Bedrock, Azure, Groq, and any LiteLLM provider.

Registered under category="llm_adapter", name="litellm".

Requires: pip install litellm  (optional — lazy import)

Config options:
    model (str):       LiteLLM model string, e.g. "openai/gpt-4o-mini"
    api_key (str):     API key (or set via environment: OPENAI_API_KEY etc.)
    temperature (float): LLM temperature (default 0.0 for deterministic mapping)
    max_tokens (int):  Max tokens per request (default 500)
    timeout (int):     Request timeout in seconds (default 30)
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from pdf_autofillr_plugins.decorators import plugin, requires
from pdf_autofillr_plugins.interfaces import PluginMetadata
from pdf_autofillr_plugins.interfaces.llm_adapter import LLMAdapter

logger = logging.getLogger(__name__)

_FIELD_MAPPING_PROMPT = """You are a PDF form field mapping assistant.

Given a list of raw PDF field names and optional context about the form,
map each field name to the most appropriate canonical schema key.

Raw PDF field names:
{fields}

Form context:
{context}

Return ONLY a valid JSON object mapping each field name to a schema key.
If you cannot confidently map a field, map it to null.

Example output:
{{"investor_full_name": "investor_name", "commitment_amount_usd": "commitment_usd", "email_addr": "email"}}

Your mapping:"""


@plugin(
    category="llm_adapter",
    name="litellm",
    version="1.0.0",
    author="Engineers Mind",
    description="Production LLM adapter via LiteLLM — OpenAI, Anthropic, Ollama, Gemini, Bedrock, and more",
    tags=["litellm", "openai", "anthropic", "ollama", "production", "builtin"],
    priority=100,
)
@requires("litellm")
class LiteLLMAdapter(LLMAdapter):
    """
    LiteLLM-powered adapter — use any supported LLM for field mapping.

    Supported providers (via LiteLLM):
        OpenAI:    model="openai/gpt-4o-mini",  api_key=OPENAI_API_KEY
        Anthropic: model="anthropic/claude-3-5-haiku-latest", api_key=ANTHROPIC_API_KEY
        Ollama:    model="ollama/llama3.2"       (no key needed)
        Google:    model="gemini/gemini-1.5-flash", api_key=GEMINI_API_KEY
        Bedrock:   model="bedrock/anthropic.claude-3-haiku-20240307-v1:0"
        Groq:      model="groq/llama-3.3-70b-versatile", api_key=GROQ_API_KEY

    Usage::

        from pdf_autofillr_plugins.builtin.llm_adapters.litellm_adapter import LiteLLMAdapter

        adapter = LiteLLMAdapter(config={
            "model": "openai/gpt-4o-mini",
            "api_key": "sk-...",
        })
        adapter.initialize()

        mapping = adapter.map_fields(
            fields=["investor_full_name", "commitment_usd", "email_addr"],
            context="LP Subscription Agreement — investor onboarding form",
        )
        # {"investor_full_name": "investor_name", "commitment_usd": "commitment_usd", ...}
    """

    def initialize(self) -> None:
        self._model = self.get_config_value("model", "openai/gpt-4o-mini")
        self._api_key = self.get_config_value("api_key", None)
        self._temperature = float(self.get_config_value("temperature", 0.0))
        self._max_tokens = int(self.get_config_value("max_tokens", 500))
        self._timeout = int(self.get_config_value("timeout", 30))
        super().initialize()
        logger.info("LiteLLMAdapter initialized with model=%s", self._model)

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="litellm",
            version="1.0.0",
            author="Engineers Mind",
            description="LiteLLM adapter — OpenAI, Anthropic, Ollama, Gemini, Bedrock, and more",
            category="llm_adapter",
            tags=["litellm", "openai", "anthropic", "ollama", "production", "builtin"],
            dependencies=["litellm"],
        )

    def map_fields(self, fields: List[str], context: str) -> Dict[str, Any]:
        """
        Map PDF field names to schema keys using the configured LLM.

        Makes one LLM call with all fields in a single prompt.
        Returns a dict of field_name → schema_key.
        """
        if not fields:
            return {}

        prompt = _FIELD_MAPPING_PROMPT.format(
            fields="\n".join(f"  - {f}" for f in fields),
            context=context or "No additional context provided.",
        )

        try:
            import litellm
            kwargs: Dict[str, Any] = {
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self._temperature,
                "max_tokens": self._max_tokens,
                "timeout": self._timeout,
            }
            if self._api_key:
                kwargs["api_key"] = self._api_key

            response = litellm.completion(**kwargs)
            raw = response.choices[0].message.content.strip()

            # Strip markdown fences if present
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            mapping = json.loads(raw)
            # Filter: only return string → string/None mappings
            return {k: v for k, v in mapping.items() if isinstance(k, str)}

        except ImportError:
            logger.error("litellm not installed — pip install litellm")
            # Fallback: passthrough
            return {f: f for f in fields}
        except json.JSONDecodeError as e:
            logger.warning("LLM returned non-JSON response: %s", e)
            return {f: f for f in fields}
        except Exception as e:
            logger.error("LiteLLMAdapter.map_fields error: %s", e)
            return {f: f for f in fields}

    def embed(self, fields: List[str], schema_keys: List[str]) -> Dict[str, Any]:
        """
        Produce embedding metadata using the LLM mapping.

        Calls map_fields() with schema_keys as context, then wraps
        results in the standard embedding metadata format.
        """
        context = f"Target schema keys: {', '.join(schema_keys)}"
        mapping = self.map_fields(fields, context)

        result = {}
        for field in fields:
            schema_key = mapping.get(field)
            result[field] = {
                "schema_key": schema_key,
                "confidence": 0.9 if schema_key and schema_key != field else 0.5,
                "field_type": "text",
                "adapter": "litellm",
                "model": self._model,
            }
        return result

    def supports_model(self, model_name: str) -> bool:
        """LiteLLM supports almost everything — return True for any non-empty model."""
        return bool(model_name)

    def get_supported_models(self) -> List[str]:
        return [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "anthropic/claude-3-5-haiku-latest",
            "anthropic/claude-3-5-sonnet-latest",
            "ollama/llama3.2",
            "ollama/mistral",
            "gemini/gemini-1.5-flash",
            "groq/llama-3.3-70b-versatile",
        ]

    def estimate_tokens(self, fields: List[str], context: str) -> int:
        prompt = _FIELD_MAPPING_PROMPT.format(
            fields="\n".join(f"  - {f}" for f in fields),
            context=context or "",
        )
        return max(1, len(prompt.split()) * 2)
