# MapperPlugin — Usage Guide

Map extracted fields to a target schema.

## Write the plugin

```python
# my_plugins/fuzzy_mapper.py
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import MapperPlugin, PluginMetadata

@plugin(category="mapper", name="fuzzy-mapper", version="1.0.0",
        author="Your Team", description="Fuzzy field mapper", priority=120)
class FuzzyMapperPlugin(MapperPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(name="fuzzy-mapper", version="1.0.0",
                              author="Your Team", description="Fuzzy mapper",
                              category="mapper")

    def supports_schema(self, schema) -> bool:
        return True

    def map_fields(self, extracted_fields, target_schema=None, **kwargs):
        schema_keys = set(target_schema.keys()) if target_schema else set()
        mapped, unmapped = {}, []
        for field in extracted_fields:
            name = field["name"]
            if name in schema_keys:
                mapped[name] = field["value"]
            else:
                unmapped.append(name)
        total = len(extracted_fields)
        return {"mapped_fields": mapped, "unmapped_fields": unmapped,
                "mapping_info": [], "mapper": "fuzzy-mapper",
                "confidence": 1.0, "coverage": len(mapped)/total if total else 0.0}
```

## Use it

```python
manager = PluginManager()
manager.discover_plugins(["my_plugins/"])

mapper = manager.find_mapper({"investor_name": "str"})
result = mapper.map_fields(
    [{"name": "investor_name", "value": "Jane", "confidence": 1.0}],
    target_schema={"investor_name": "str"},
)
print(result["mapped_fields"])  # {"investor_name": "Jane"}
```
