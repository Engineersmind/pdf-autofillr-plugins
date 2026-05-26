# FillerPlugin — Usage Guide

Fill a PDF template with data using your own strategy.

## Write the plugin

```python
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import FillerPlugin, PluginMetadata

@plugin(category="filler", name="my-filler", version="1.0.0",
        author="Your Team", description="Custom PDF filler")
class MyFillerPlugin(FillerPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(name="my-filler", version="1.0.0",
                              author="Your Team", description="Custom filler",
                              category="filler")

    def supports_pdf_type(self, pdf_path: str) -> bool:
        return pdf_path.endswith(".pdf")

    def fill(self, pdf_path: str, data: dict, output_path=None, **kwargs):
        out = output_path or pdf_path.replace(".pdf", "_filled.pdf")
        # Replace with real PDF filling logic (e.g. PyMuPDF, pdfrw)
        return {"output_path": out, "filled_fields": list(data.keys()),
                "unfilled_fields": [], "filler": "my-filler"}
```
