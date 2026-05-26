# Writing a Plugin

→ For the full guide with all 10 plugin types, see [plugins/USAGE.md](../../plugins/USAGE.md).

## Minimum structure

Every plugin:

1. Inherits from one of the interface classes in `pdf_autofillr_plugins.interfaces`
2. Is decorated with `@plugin(category=..., name=...)`
3. Implements `get_metadata()` and all abstract methods from the interface

```python
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(
    category="validator",
    name="my-validator",
    version="1.0.0",
    author="Your Team",
    description="Validates something useful",
    tags=["custom"],
    priority=100,
)
class MyValidator(ValidatorPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-validator", version="1.0.0",
            author="Your Team", description="Validates something useful",
            category="validator",
        )

    def supports_field_type(self, field_type: str) -> bool:
        return field_type.lower() == "my_field_type"

    def validate(self, field_name, field_value, rules=None, **kwargs):
        valid = field_value is not None
        return {
            "valid": valid,
            "errors": [] if valid else ["Value cannot be None"],
            "warnings": [],
            "validator": "my-validator",
            "field_name": field_name,
        }
```

## Plugin types and their abstract methods

| Interface | Abstract methods |
|-----------|-----------------|
| `ExtractorPlugin` | `extract()`, `supports()` |
| `MapperPlugin` | `map_fields()`, `supports_schema()` |
| `ValidatorPlugin` | `validate()`, `supports_field_type()` |
| `FillerPlugin` | `fill()`, `supports_pdf_type()` |
| `ChunkerPlugin` | `chunk()` |
| `EmbedderPlugin` | `embed()`, `check()` |
| `TransformerPlugin` | `transform()`, `supports_type()` |
| `LLMAdapter` | `map_fields()`, `embed()` |
| `OutputFormatterPlugin` | `format()` |
| `DataConnectorPlugin` | `fetch()` |

## Configuration

Plugins receive an optional `config` dict at load time:

```python
manager.load_plugin("my-validator", "validator", config={"api_key": "sk-..."})

# In your plugin:
def initialize(self):
    self.api_key = self.get_config_value("api_key", "")
    super().initialize()
```

## Usage guide files

After running `pdf-autofillr-plugins setup`, per-type guides are in `usage/`:

- `usage/validator.md` — ValidatorPlugin walkthrough
- `usage/extractor.md` — ExtractorPlugin walkthrough
- `usage/mapper.md` — MapperPlugin walkthrough
- etc.
