"""
Plugin interface classes — import from here.

    from pdf_autofillr_plugins.interfaces import (
        BasePlugin, PluginMetadata,
        LLMAdapter,
        ExtractorPlugin,
        MapperPlugin,
        ValidatorPlugin,
        FillerPlugin,
        ChunkerPlugin,
        EmbedderPlugin,
        TransformerPlugin,
        OutputFormatterPlugin,
        DataConnectorPlugin,
    )
"""

from pdf_autofillr_plugins.interfaces.base_plugin import BasePlugin, PluginMetadata
from pdf_autofillr_plugins.interfaces.llm_adapter import LLMAdapter
from pdf_autofillr_plugins.interfaces.extractor_plugin import ExtractorPlugin
from pdf_autofillr_plugins.interfaces.mapper_plugin import MapperPlugin
from pdf_autofillr_plugins.interfaces.validator_plugin import ValidatorPlugin
from pdf_autofillr_plugins.interfaces.filler_plugin import FillerPlugin
from pdf_autofillr_plugins.interfaces.chunker_plugin import ChunkerPlugin
from pdf_autofillr_plugins.interfaces.embedder_plugin import EmbedderPlugin
from pdf_autofillr_plugins.interfaces.transformer_plugin import TransformerPlugin
from pdf_autofillr_plugins.interfaces.output_formatter import OutputFormatterPlugin
from pdf_autofillr_plugins.interfaces.data_connector import DataConnectorPlugin

__all__ = [
    "BasePlugin",
    "PluginMetadata",
    "LLMAdapter",
    "ExtractorPlugin",
    "MapperPlugin",
    "ValidatorPlugin",
    "FillerPlugin",
    "ChunkerPlugin",
    "EmbedderPlugin",
    "TransformerPlugin",
    "OutputFormatterPlugin",
    "DataConnectorPlugin",
]
