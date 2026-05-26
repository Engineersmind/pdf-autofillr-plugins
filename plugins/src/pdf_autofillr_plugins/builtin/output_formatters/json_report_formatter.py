"""
Built-in: JSONReportFormatter

Wraps the filled PDF bytes in a JSON-serialisable report envelope,
including field coverage, fill status, and audit metadata.

This is the output formatter Sir described in the original README::

    class JSONReportFormatter(OutputFormatterPlugin):
        name = "json-report"

        def format(self, filled_pdf: bytes, field_map: dict) -> dict:
            return {"pdf": filled_pdf, "report": field_map, "status": "ok"}

Registered under category="output_formatter", name="json-report".
"""
from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any, Dict

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import PluginMetadata
from pdf_autofillr_plugins.interfaces.output_formatter import OutputFormatterPlugin


@plugin(
    category="output_formatter",
    name="json-report",
    version="1.0.0",
    author="Engineers Mind",
    description="Wraps filled PDF in a JSON report with field coverage and audit metadata",
    tags=["json", "report", "audit", "builtin"],
    priority=100,
)
class JSONReportFormatter(OutputFormatterPlugin):
    """
    JSON report output formatter.

    Returns a dict containing:
    - pdf_b64:      base64-encoded filled PDF (safe for JSON serialisation)
    - pdf_bytes:    raw PDF bytes (for in-process use)
    - report:       field_name → value map
    - status:       "ok" or "partial"
    - field_count:  number of fields filled
    - timestamp:    ISO 8601 fill timestamp
    - formatter:    "json-report"

    Config options:
        include_pdf_bytes (bool): Include raw bytes (default True)
        include_b64 (bool):       Include base64 PDF (default True)
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="json-report",
            version="1.0.0",
            author="Engineers Mind",
            description="Wraps filled PDF in a JSON report with field coverage and audit metadata",
            category="output_formatter",
            tags=["json", "report", "audit", "builtin"],
        )

    def format(
        self,
        filled_pdf: bytes,
        field_map: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Format filled PDF and field data into a JSON report envelope.

        Args:
            filled_pdf: Raw bytes of the filled PDF
            field_map:  Dict of field_name → value written into the PDF
            **kwargs:   Optional: session_id, user_id, pdf_path, unfilled_fields

        Returns:
            Dict with pdf_b64, report, status, field_count, timestamp
        """
        unfilled = kwargs.get("unfilled_fields", [])
        status = "ok" if not unfilled else "partial"

        result: Dict[str, Any] = {
            "status": status,
            "field_count": len(field_map),
            "unfilled_count": len(unfilled),
            "unfilled_fields": unfilled,
            "report": field_map,
            "formatter": "json-report",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        if kwargs.get("session_id"):
            result["session_id"] = kwargs["session_id"]
        if kwargs.get("user_id"):
            result["user_id"] = kwargs["user_id"]
        if kwargs.get("pdf_path"):
            result["pdf_path"] = kwargs["pdf_path"]

        include_bytes = self.get_config_value("include_pdf_bytes", True)
        include_b64 = self.get_config_value("include_b64", True)

        if include_bytes:
            result["pdf_bytes"] = filled_pdf
        if include_b64:
            result["pdf_b64"] = base64.b64encode(filled_pdf).decode("utf-8")

        return result

    def supports_format(self, format_name: str) -> bool:
        return format_name.lower() in {"json", "json-report", "report"}

    def get_supported_formats(self):
        return ["json", "json-report", "report"]
