"""
Built-in: InvoiceExtractorPlugin

Specialized extractor for invoice PDFs. Activates automatically when the
PDF path contains "invoice". In production, replace the stub extract()
body with real PyMuPDF / pdfplumber parsing.

Registered under category="extractor", name="invoice-extractor".
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import ExtractorPlugin, PluginMetadata


@plugin(
    category="extractor",
    name="invoice-extractor",
    version="1.0.0",
    author="PDF AutoFillr Team",
    description="Extracts common invoice fields (number, date, vendor, total) from invoice PDFs",
    tags=["invoice", "financial", "builtin"],
    priority=200,  # higher than default (100) — wins over generic extractors
)
class InvoiceExtractorPlugin(ExtractorPlugin):
    """
    Invoice PDF extractor.

    Activates for any PDF whose path contains the word "invoice".
    Returns a standardised set of invoice fields.

    Fields extracted:
    - invoice_number  (text)
    - invoice_date    (date)
    - vendor_name     (text)
    - total_amount    (currency)

    To extend: override extract() with real PDF parsing logic using
    PyMuPDF, pdfplumber, or a custom template engine.
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="invoice-extractor",
            version="1.0.0",
            author="PDF AutoFillr Team",
            description="Extracts common invoice fields from invoice PDFs",
            category="extractor",
            tags=["invoice", "financial", "builtin"],
        )

    def supports(self, pdf_path: str, **kwargs) -> bool:
        """Activate when the filename contains 'invoice'."""
        return "invoice" in pdf_path.lower()

    def extract(
        self,
        pdf_path: str,
        strategy: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Extract invoice fields from PDF.

        Returns stub data by default. Replace with real parsing in production:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            text = doc[0].get_text()
            # ... parse text for invoice fields
        """
        fields: List[Dict[str, Any]] = [
            {
                "name": "invoice_number",
                "value": self.get_config_value("default_invoice_number", "INV-2026-001"),
                "type": "text",
                "confidence": 0.95,
                "bbox": [100, 50, 200, 70],
            },
            {
                "name": "invoice_date",
                "value": self.get_config_value("default_invoice_date", "2026-04-30"),
                "type": "date",
                "confidence": 0.98,
                "bbox": [100, 80, 200, 100],
            },
            {
                "name": "vendor_name",
                "value": self.get_config_value("default_vendor_name", "Acme Corporation"),
                "type": "text",
                "confidence": 0.92,
                "bbox": [100, 110, 300, 130],
            },
            {
                "name": "total_amount",
                "value": self.get_config_value("default_total_amount", "1234.56"),
                "type": "currency",
                "confidence": 0.99,
                "bbox": [400, 500, 500, 520],
            },
        ]

        return {
            "fields": fields,
            "metadata": {
                "pdf_path": pdf_path,
                "page_count": 1,
                "document_type": "invoice",
                "strategy": strategy or "template",
            },
            "extractor": "invoice-extractor",
            "confidence": 0.96,
        }

    def get_supported_strategies(self) -> List[str]:
        return ["template", "ml", "hybrid"]
