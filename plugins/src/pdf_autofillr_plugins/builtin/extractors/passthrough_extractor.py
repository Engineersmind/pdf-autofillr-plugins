"""
Built-in: PassthroughExtractorPlugin

Returns fields as-is. Useful as a base / no-op extractor for testing.
Registered under category="extractor", name="passthrough-extractor".
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import ExtractorPlugin, PluginMetadata


@plugin(
    category="extractor",
    name="passthrough-extractor",
    version="1.0.0",
    author="PDF AutoFillr Team",
    description="No-op extractor — returns pre-supplied fields unchanged. Useful for testing.",
    tags=["passthrough", "testing", "builtin"],
    priority=1,  # lowest priority — real extractors should always win
)
class PassthroughExtractorPlugin(ExtractorPlugin):
    """
    No-op extractor.

    Instead of parsing a PDF, it returns whatever fields were passed in via
    config['fields']. Handy for unit tests and pipeline development without
    needing a real PDF.

    Config:
        fields (list[dict]): pre-built field list to return from extract()
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="passthrough-extractor",
            version="1.0.0",
            author="PDF AutoFillr Team",
            description="No-op extractor — returns pre-supplied fields unchanged",
            category="extractor",
            tags=["passthrough", "testing", "builtin"],
        )

    def supports(self, pdf_path: str, **kwargs) -> bool:
        # Only activates when explicitly configured
        return bool(self.config.get("fields"))

    def extract(
        self,
        pdf_path: str,
        strategy: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        fields: List[Dict[str, Any]] = self.config.get("fields", [])
        return {
            "fields": fields,
            "metadata": {
                "pdf_path": pdf_path,
                "strategy": strategy or "passthrough",
                "field_count": len(fields),
            },
            "extractor": "passthrough-extractor",
            "confidence": 1.0,
        }

    def get_supported_strategies(self) -> List[str]:
        return ["passthrough"]
