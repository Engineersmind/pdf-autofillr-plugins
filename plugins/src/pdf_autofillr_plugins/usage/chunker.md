# ChunkerPlugin — Usage Guide

Split PDFs into logical chunks for large document processing.

## Write the plugin

```python
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import ChunkerPlugin, PluginMetadata

@plugin(category="chunker", name="page-chunker", version="1.0.0",
        author="Your Team", description="Splits PDF into one chunk per page")
class PageChunkerPlugin(ChunkerPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(name="page-chunker", version="1.0.0",
                              author="Your Team", description="One chunk per page",
                              category="chunker")

    def chunk(self, pdf_path: str, chunk_size=None, **kwargs):
        # Replace with real PyMuPDF page splitting
        return [
            {"chunk_id": f"page_{i}", "content": f"Page {i} content",
             "page_numbers": [i], "metadata": {"page": i}}
            for i in range(1, 4)  # stub: 3 pages
        ]
```
