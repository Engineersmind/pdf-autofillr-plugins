"""
Example: writing a custom ExtractorPlugin.

    python examples/custom_extractor.py
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pdf_autofillr_plugins import PluginManager, plugin
from pdf_autofillr_plugins.interfaces import ExtractorPlugin, PluginMetadata


@plugin(
    category="extractor",
    name="invoice-extractor",
    version="1.0.0",
    author="Your Team",
    description="Extracts common invoice fields from invoice PDFs",
    tags=["invoice", "financial"],
    priority=200,  # higher than default (100) — loads before generic extractors
)
class InvoiceExtractorPlugin(ExtractorPlugin):
    """
    Specialised extractor for invoice PDFs.

    Activate when the PDF path/name contains 'invoice'. In production you
    would use PyMuPDF or pdfplumber to actually parse the file.
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="invoice-extractor",
            version="1.0.0",
            author="Your Team",
            description="Extracts common invoice fields from invoice PDFs",
            category="extractor",
            tags=["invoice", "financial"],
        )

    def supports(self, pdf_path: str, **kwargs) -> bool:
        return "invoice" in pdf_path.lower()

    def extract(
        self,
        pdf_path: str,
        strategy: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        # In production: parse the actual PDF here
        fields: List[Dict[str, Any]] = [
            {
                "name": "invoice_number",
                "value": "INV-2026-001",
                "type": "text",
                "confidence": 0.97,
            },
            {
                "name": "invoice_date",
                "value": "2026-04-30",
                "type": "date",
                "confidence": 0.98,
            },
            {
                "name": "vendor_name",
                "value": "Acme Corp",
                "type": "text",
                "confidence": 0.95,
            },
            {
                "name": "total_amount",
                "value": "1234.56",
                "type": "currency",
                "confidence": 0.99,
            },
        ]
        return {
            "fields": fields,
            "metadata": {"pdf_path": pdf_path, "document_type": "invoice"},
            "extractor": "invoice-extractor",
            "confidence": 0.97,
        }

    def get_supported_strategies(self) -> List[str]:
        return ["template", "ml", "hybrid"]


if __name__ == "__main__":
    manager = PluginManager()
    manager.registry.register_plugin(
        InvoiceExtractorPlugin, "extractor", "invoice-extractor"
    )

    # find_extractor uses supports() to pick the right plugin automatically
    extractor = manager.find_extractor("quarterly_invoice.pdf")
    if extractor:
        result = extractor.extract("quarterly_invoice.pdf")
        print(f"\nExtracted {len(result['fields'])} fields from invoice:")
        for f in result["fields"]:
            print(f"  {f['name']:<20} = {f['value']}  ({f['confidence']:.0%})")
    else:
        print("No extractor matched this PDF.")
    print()
