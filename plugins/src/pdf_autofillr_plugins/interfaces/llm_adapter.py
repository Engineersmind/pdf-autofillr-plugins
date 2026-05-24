"""
LLMAdapter — Plugin interface for custom LLM providers.

This is the flagship plugin type for pdf-autofillr-plugins.

Implement LLMAdapter to plug in any LLM (local, fine-tuned, cloud, or
proprietary) into the pdf-autofillr mapping pipeline. The adapter is
called by the mapper module to:

  1. map_fields()  — map extracted PDF field names to schema keys using LLM
  2. embed()       — produce embedding metadata baked into the PDF template

Sir's original vision (from pdf-autofillr-plugins README):

    from pdf_autofillr_plugins.interfaces import LLMAdapter

    class MyCustomLLM(LLMAdapter):
        def map_fields(self, fields: list[str], context: str) -> dict:
            return {field: self.call_my_llm(field, context) for field in fields}

Official adapters (planned):
    pdf-autofillr-plugin-openai     — GPT-4o/4o-mini
    pdf-autofillr-plugin-anthropic  — Claude
    pdf-autofillr-plugin-ollama     — local Ollama models
    pdf-autofillr-plugin-google     — Gemini
"""
from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List

from pdf_autofillr_plugins.interfaces.base_plugin import BasePlugin, PluginMetadata


class LLMAdapter(BasePlugin):
    """
    Base class for LLM adapter plugins.

    LLM adapters let you use any language model for PDF field mapping.
    Implement this interface to replace the default LiteLLM routing with
    your own model, API, or local inference engine.

    Minimum implementation::

        from pdf_autofillr_plugins import plugin
        from pdf_autofillr_plugins.interfaces import LLMAdapter, PluginMetadata

        @plugin(category="llm_adapter", name="my-llm")
        class MyLLM(LLMAdapter):

            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="my-llm", version="1.0.0",
                    author="Your Team", description="My custom LLM",
                    category="llm_adapter",
                )

            def map_fields(self, fields: list[str], context: str) -> dict:
                return {field: self.call_my_api(field, context) for field in fields}

            def embed(self, fields: list[str], schema_keys: list[str]) -> dict:
                return {field: schema_keys[i % len(schema_keys)]
                        for i, field in enumerate(fields)}
    """

    @abstractmethod
    def map_fields(self, fields: List[str], context: str) -> Dict[str, Any]:
        """
        Map extracted PDF field names to schema keys using this LLM.

        This is the core method — called once per PDF template embed.
        Each extracted field name is mapped to a canonical schema key.

        Args:
            fields:  List of raw PDF field names extracted from the form
                     (e.g. ["investor_full_name", "commitment_amount_usd"])
            context: Additional context about the form (page text, section
                     headers, document type, etc.)

        Returns:
            Dict mapping each field name to a predicted schema key::

                {
                    "investor_full_name":    "investor_name",
                    "commitment_amount_usd": "commitment_usd",
                    "email_addr":            "email",
                }

        Unmapped fields should be omitted or mapped to None.
        """
        pass

    @abstractmethod
    def embed(self, fields: List[str], schema_keys: List[str]) -> Dict[str, Any]:
        """
        Produce embedding metadata baked into the PDF template.

        Called after map_fields() to generate the metadata that is
        stored in the embedded PDF. This metadata is used later at
        fill time to write values directly without re-running the LLM.

        Args:
            fields:      List of raw PDF field names
            schema_keys: List of canonical schema keys (your target schema)

        Returns:
            Dict of embedding metadata::

                {
                    "investor_full_name": {
                        "schema_key":  "investor_name",
                        "confidence":  0.97,
                        "field_type":  "text",
                    },
                    ...
                }
        """
        pass

    def supports_model(self, model_name: str) -> bool:
        """
        Check if this adapter supports a given model name.

        Args:
            model_name: Model identifier (e.g. "gpt-4o", "claude-3-5-sonnet")

        Returns:
            True if this adapter can handle the model
        """
        return False

    def get_supported_models(self) -> List[str]:
        """
        Return list of model names this adapter supports.

        Returns:
            List of model name strings (e.g. ["gpt-4o", "gpt-4o-mini"])
        """
        return []

    def estimate_tokens(self, fields: List[str], context: str) -> int:
        """
        Estimate token count for a map_fields() call.

        Useful for cost estimation before making the API call.

        Args:
            fields:  Field names list
            context: Context string

        Returns:
            Estimated token count (rough)
        """
        text = " ".join(fields) + " " + context
        return max(1, len(text.split()) * 2)

    def get_metadata(self) -> PluginMetadata:
        """Default metadata — override with your own."""
        return PluginMetadata(
            name=self.__class__.__name__,
            version="1.0.0",
            author="Unknown",
            description="Custom LLM adapter",
            category="llm_adapter",
        )
