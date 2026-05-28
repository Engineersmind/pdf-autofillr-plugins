"""
OutputFormatterPlugin — Plugin interface for custom output formatters.

Control how filled PDFs and their metadata are packaged and returned.
Use this to produce JSON reports, audit trails, annotated PDFs, or
any custom output format alongside the filled PDF bytes.

Sir's original vision::

    class JSONReportFormatter(OutputFormatterPlugin):
        name = "json-report"

        def format(self, filled_pdf: bytes, field_map: dict) -> dict:
            return {"pdf": filled_pdf, "report": field_map, "status": "ok"}
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List

from pdf_autofillr_plugins.interfaces.base_plugin import BasePlugin, PluginMetadata


class OutputFormatterPlugin(BasePlugin):
    """
    Base class for output formatter plugins.

    Output formatters control what gets returned after a PDF is filled.
    By default pdf-autofillr returns the filled PDF bytes. Use this
    interface to add JSON reports, audit trails, field coverage summaries,
    annotated PDFs, or any envelope format your downstream system expects.

    Minimum implementation::

        from pdf_autofillr_plugins import plugin
        from pdf_autofillr_plugins.interfaces import OutputFormatterPlugin, PluginMetadata

        @plugin(category="output_formatter", name="json-report")
        class JSONReportFormatter(OutputFormatterPlugin):

            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="json-report", version="1.0.0",
                    author="Your Team", description="Wraps filled PDF in JSON report",
                    category="output_formatter",
                )

            def format(self, filled_pdf: bytes, field_map: dict) -> dict:
                return {
                    "pdf": filled_pdf,
                    "report": field_map,
                    "status": "ok",
                    "field_count": len(field_map),
                }
    """

    @abstractmethod
    def format(
        self,
        filled_pdf: bytes,
        field_map: Dict[str, Any],
        **kwargs,
    ) -> Any:
        """
        Format the filled PDF and its field data into your desired output.

        Args:
            filled_pdf: Raw bytes of the filled PDF
            field_map:  Dict of field_name → value that was written into the PDF
            **kwargs:   Additional context (session_id, user_id, pdf_path, etc.)

        Returns:
            Your formatted output — dict, bytes, str, or any serialisable type.
            Common patterns:
            - Dict with "pdf" + "report" keys
            - JSON string
            - Tuple of (pdf_bytes, report_dict)
        """
        pass

    def supports_format(self, format_name: str) -> bool:
        """
        Check if this formatter supports a named output format.

        Args:
            format_name: e.g. "json", "pdf+json", "audit_trail"

        Returns:
            True if supported
        """
        return False

    def get_supported_formats(self) -> List[str]:
        """
        List output formats this formatter can produce.

        Returns:
            List of format name strings
        """
        return ["default"]

    def get_metadata(self) -> PluginMetadata:
        """Default metadata — override with your own."""
        return PluginMetadata(
            name=self.__class__.__name__,
            version="1.0.0",
            author="Unknown",
            description="Custom output formatter",
            category="output_formatter",
        )
