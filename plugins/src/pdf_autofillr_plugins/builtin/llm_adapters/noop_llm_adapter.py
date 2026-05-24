"""
Built-in: NoOpLLMAdapter

Passthrough LLM adapter — returns fields unchanged (exact name match).
Used for testing and as a baseline. No API calls, no dependencies.

Registered under category="llm_adapter", name="noop-llm".
"""
from __future__ import annotations

from typing import Any, Dict, List

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import PluginMetadata
from pdf_autofillr_plugins.interfaces.llm_adapter import LLMAdapter


@plugin(
    category="llm_adapter",
    name="noop-llm",
    version="1.0.0",
    author="Engineers Mind",
    description="No-op LLM adapter — maps fields by exact name match. No API calls. Use for testing.",
    tags=["noop", "testing", "builtin"],
    priority=1,
)
class NoOpLLMAdapter(LLMAdapter):
    """
    No-op (passthrough) LLM adapter.

    Maps each field to itself by exact name match.
    If a schema_key list is provided via config, maps sequentially.
    Useful as a testing baseline — no LLM, no API key, no network.

    Config options:
        mapping (dict): Optional override mapping {field_name: schema_key}.
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="noop-llm",
            version="1.0.0",
            author="Engineers Mind",
            description="No-op LLM adapter — passthrough field mapping for testing",
            category="llm_adapter",
            tags=["noop", "testing", "builtin"],
        )

    def map_fields(self, fields: List[str], context: str) -> Dict[str, Any]:
        """
        Map each field to itself (exact name passthrough).

        If config['mapping'] is provided, uses that dict for overrides.
        """
        override = self.get_config_value("mapping", {})
        return {field: override.get(field, field) for field in fields}

    def embed(self, fields: List[str], schema_keys: List[str]) -> Dict[str, Any]:
        """
        Produce embedding metadata by matching fields to schema_keys positionally.
        """
        result = {}
        for i, field in enumerate(fields):
            key = schema_keys[i] if i < len(schema_keys) else field
            result[field] = {
                "schema_key": key,
                "confidence": 1.0,
                "field_type": "text",
                "adapter": "noop-llm",
            }
        return result

    def supports_model(self, model_name: str) -> bool:
        return model_name in ("noop", "passthrough", "")

    def get_supported_models(self) -> List[str]:
        return ["noop", "passthrough"]
