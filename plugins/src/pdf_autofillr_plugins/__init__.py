"""
pdf-autofillr-plugins
=====================
Plugin framework for extending pdf-autofillr modules.

Sir's vision — the flagship plugin type::

    from pdf_autofillr_plugins import plugin, PluginManager
    from pdf_autofillr_plugins.interfaces import LLMAdapter, PluginMetadata

    @plugin(category="llm_adapter", name="my-custom-llm")
    class MyCustomLLM(LLMAdapter):

        def get_metadata(self) -> PluginMetadata:
            return PluginMetadata(name="my-custom-llm", version="1.0.0",
                                  author="Your Team", description="My LLM",
                                  category="llm_adapter")

        def map_fields(self, fields: list[str], context: str) -> dict:
            # Your custom LLM mapping logic
            return {field: self.call_my_llm(field, context) for field in fields}

        def embed(self, fields: list[str], schema_keys: list[str]) -> dict:
            return {field: {"schema_key": schema_keys[i], "confidence": 0.9}
                    for i, field in enumerate(fields)}

All plugin types::

    from pdf_autofillr_plugins.interfaces import (
        LLMAdapter,           # Use any LLM for field mapping (flagship)
        ExtractorPlugin,      # Custom PDF field extraction
        MapperPlugin,         # Custom field-to-schema mapping
        ValidatorPlugin,      # Custom field validation
        FillerPlugin,         # Custom PDF filling
        TransformerPlugin,    # Pre/post-process field values
        ChunkerPlugin,        # Custom PDF chunking
        EmbedderPlugin,       # Custom metadata embedding
        OutputFormatterPlugin, # Control output format
        DataConnectorPlugin,  # Pull data from CRMs/APIs/databases
    )

Built-in plugins ready to use::

    from pdf_autofillr_plugins.builtin.llm_adapters.noop_llm_adapter import NoOpLLMAdapter
    from pdf_autofillr_plugins.builtin.llm_adapters.litellm_adapter import LiteLLMAdapter
    from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
    from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import PassthroughExtractorPlugin
    from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import InvoiceExtractorPlugin
    from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
    from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin
    from pdf_autofillr_plugins.builtin.output_formatters.json_report_formatter import JSONReportFormatter
    from pdf_autofillr_plugins.builtin.output_formatters.passthrough_formatter import PassthroughFormatter
    from pdf_autofillr_plugins.builtin.data_connectors.dict_connector import DictConnector
    from pdf_autofillr_plugins.builtin.data_connectors.json_file_connector import JSONFileConnector
"""

__version__ = "0.2.0"

from pdf_autofillr_plugins.decorators import plugin, requires
from pdf_autofillr_plugins.interfaces.base_plugin import BasePlugin, PluginMetadata
from pdf_autofillr_plugins.manager import PluginManager
from pdf_autofillr_plugins.registry import PluginRegistry

__all__ = [
    "plugin",
    "requires",
    "PluginRegistry",
    "PluginManager",
    "BasePlugin",
    "PluginMetadata",
]
