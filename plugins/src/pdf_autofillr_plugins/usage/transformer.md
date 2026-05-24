# TransformerPlugin — Usage Guide

Pre/post-process field values (format normalization, enrichment, masking).

## Write the plugin

```python
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import TransformerPlugin, PluginMetadata

@plugin(category="transformer", name="date-normalizer", version="1.0.0",
        author="Your Team", description="Normalizes date values to ISO 8601")
class DateNormalizerPlugin(TransformerPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(name="date-normalizer", version="1.0.0",
                              author="Your Team", description="ISO 8601 date normalizer",
                              category="transformer")

    def supports_type(self, value_type: type) -> bool:
        return value_type in {str}

    def transform(self, value, transform_type=None, **kwargs):
        from datetime import datetime
        for fmt in ("%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d", "%B %d, %Y"):
            try:
                return datetime.strptime(str(value), fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return value  # return unchanged if no format matched
```

## Use it

```python
manager = PluginManager()
manager.discover_plugins(["my_plugins/"])

transformer = manager.load_plugin("date-normalizer", "transformer")
print(transformer.transform("12/25/2026"))  # "2026-12-25"
```
