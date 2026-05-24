# EmbedderPlugin — Usage Guide

Embed custom metadata into PDFs or check for existing metadata.

## Write the plugin

```python
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import EmbedderPlugin, PluginMetadata

@plugin(category="embedder", name="xmp-embedder", version="1.0.0",
        author="Your Team", description="Embeds metadata as XMP into PDFs")
class XMPEmbedderPlugin(EmbedderPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(name="xmp-embedder", version="1.0.0",
                              author="Your Team", description="XMP metadata embedder",
                              category="embedder")

    def embed(self, pdf_path: str, metadata: dict, output_path=None, **kwargs):
        out = output_path or pdf_path.replace(".pdf", "_embedded.pdf")
        # Replace with real XMP embedding logic
        return {"output_path": out, "embedded_keys": list(metadata.keys()),
                "embedder": "xmp-embedder"}

    def check(self, pdf_path: str, **kwargs):
        # Replace with real XMP extraction
        return {"has_metadata": False, "metadata": {}, "embedded_keys": []}
```
