# ExtractorPlugin — Usage Guide

Extract structured field data from a PDF or document.

## Write the plugin

```python
# my_plugins/contract_extractor.py
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import ExtractorPlugin, PluginMetadata

@plugin(category="extractor", name="contract-extractor", version="1.0.0",
        author="Your Team", description="Extracts fields from contract PDFs", priority=200)
class ContractExtractorPlugin(ExtractorPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(name="contract-extractor", version="1.0.0",
                              author="Your Team", description="Contract field extractor",
                              category="extractor")

    def supports(self, pdf_path: str, **kwargs) -> bool:
        return "contract" in pdf_path.lower()

    def extract(self, pdf_path: str, strategy=None, **kwargs):
        # Replace this stub with real PyMuPDF / pdfplumber parsing
        fields = [
            {"name": "party_name", "value": "Acme Corp", "type": "text", "confidence": 0.95},
            {"name": "contract_date", "value": "2026-01-15", "type": "date", "confidence": 0.98},
        ]
        return {"fields": fields, "metadata": {"pdf_path": pdf_path},
                "extractor": "contract-extractor", "confidence": 0.96}
```

## Use it

```python
manager = PluginManager()
manager.discover_plugins(["my_plugins/"])

extractor = manager.find_extractor("service_contract.pdf")
if extractor:
    result = extractor.extract("service_contract.pdf")
    for f in result["fields"]:
        print(f["name"], "=", f["value"])
```
