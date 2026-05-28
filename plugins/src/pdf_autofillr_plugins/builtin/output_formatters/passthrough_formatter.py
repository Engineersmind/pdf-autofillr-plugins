"""
Built-in: PassthroughFormatter

Returns the filled PDF bytes unchanged — no envelope, no wrapping.
This is the default behaviour when no formatter is configured.

Registered under category="output_formatter", name="passthrough-formatter".
"""

from __future__ import annotations

from typing import Any, Dict

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import PluginMetadata
from pdf_autofillr_plugins.interfaces.output_formatter import OutputFormatterPlugin


@plugin(
    category="output_formatter",
    name="passthrough-formatter",
    version="1.0.0",
    author="Engineers Mind",
    description="Returns filled PDF bytes unchanged — default output format",
    tags=["passthrough", "default", "builtin"],
    priority=1,
)
class PassthroughFormatter(OutputFormatterPlugin):
    """
    Passthrough output formatter — returns PDF bytes as-is.

    Use as the default when no formatting is needed.
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="passthrough-formatter",
            version="1.0.0",
            author="Engineers Mind",
            description="Returns filled PDF bytes unchanged — default output format",
            category="output_formatter",
            tags=["passthrough", "default", "builtin"],
        )

    def format(self, filled_pdf: bytes, field_map: Dict[str, Any], **kwargs) -> bytes:
        """Return the filled PDF bytes unchanged."""
        return filled_pdf

    def supports_format(self, format_name: str) -> bool:
        return format_name.lower() in {"passthrough", "raw", "bytes"}

    def get_supported_formats(self):
        return ["passthrough", "raw", "bytes"]
