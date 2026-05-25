# pdf-autofillr-plugins — Complete Usage Guide

> Full reference for writing, registering, discovering, and using plugins.

---

## Table of Contents

1. [Install](#1-install)
2. [Core concepts](#2-core-concepts)
3. [Writing a plugin](#3-writing-a-plugin)
4. [Plugin interfaces](#4-plugin-interfaces)
5. [The @plugin decorator](#5-the-plugin-decorator)
6. [PluginRegistry](#6-pluginregistry)
7. [PluginManager](#7-pluginmanager)
8. [Built-in plugins](#8-built-in-plugins)
9. [Examples](#9-examples)
10. [Integration with pdf-autofillr modules](#10-integration-with-pdf-autofillr-modules)
11. [Testing your plugins](#11-testing-your-plugins)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Install

```bash
pip install pdf-autofillr-plugins      # production
pip install "pdf-autofillr-plugins[dev]"  # + dev tools
```

Zero runtime dependencies. Pure Python 3.9+.

---

## 2. Core concepts

| Concept | Class | Description |
|---|---|---|
| Interface | `BasePlugin` + subclasses | ABCs that define what a plugin must implement |
| Decorator | `@plugin(...)` | Stamps metadata onto a class so the registry can find it |
| Registry | `PluginRegistry` | Discovers and stores plugin classes |
| Manager | `PluginManager` | Loads, caches, and runs plugin instances |

The typical flow:

```
Write plugin class → decorate with @plugin → register or auto-discover → load via PluginManager → call plugin methods
```

---

## 3. Writing a plugin

Every plugin:

1. Inherits from one of the interface classes
2. Is decorated with `@plugin`
3. Implements `get_metadata()` and the interface's abstract methods

Minimal example:

```python
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(category="validator", name="my-validator", version="1.0.0", author="You")
class MyValidator(ValidatorPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-validator",
            version="1.0.0",
            author="You",
            description="Does something useful",
            category="validator",
        )

    def supports_field_type(self, field_type: str) -> bool:
        return field_type.lower() == "my_field_type"

    def validate(self, field_name, field_value, rules=None, **kwargs):
        # your validation logic here
        valid = field_value is not None
        return {
            "valid": valid,
            "errors": [] if valid else ["Value is None"],
            "warnings": [],
            "validator": "my-validator",
        }
```

### Plugin lifecycle

```python
plugin_instance.initialize()   # called once when loaded — set up resources
plugin_instance.validate(...)  # your business logic
plugin_instance.shutdown()     # called when unloaded — clean up resources
```

Override `initialize()` and `shutdown()` when you have external connections, models, or file handles to manage.

### Using configuration

Plugins receive an optional `config` dict at instantiation:

```python
@plugin(category="validator", name="api-validator")
class ApiValidatorPlugin(ValidatorPlugin):

    def initialize(self):
        self.api_url = self.get_config_value("api_url", "https://api.example.com")
        self.api_key = self.get_config_value("api_key", "")
        super().initialize()

    def validate(self, field_name, field_value, rules=None, **kwargs):
        # use self.api_url and self.api_key
        ...
```

Load with config:

```python
manager.load_plugin("api-validator", "validator", config={
    "api_url": "https://myapi.com",
    "api_key": os.getenv("MY_VALIDATOR_API_KEY"),
})
```

---

## 4. Plugin interfaces

### ExtractorPlugin

Extracts structured field data from a PDF or document.

```python
from pdf_autofillr_plugins.interfaces import ExtractorPlugin, PluginMetadata

@plugin(category="extractor", name="my-extractor")
class MyExtractor(ExtractorPlugin):

    def get_metadata(self) -> PluginMetadata: ...

    def supports(self, pdf_path: str, **kwargs) -> bool:
        """Return True if this plugin can handle the given PDF."""
        return "invoice" in pdf_path.lower()

    def extract(self, pdf_path: str, strategy=None, **kwargs) -> dict:
        """Extract fields from the PDF. Return a dict with 'fields' list."""
        fields = [
            {"name": "invoice_number", "value": "INV-001", "type": "text", "confidence": 0.97},
        ]
        return {
            "fields": fields,
            "metadata": {"pdf_path": pdf_path},
            "extractor": "my-extractor",
            "confidence": 0.97,
        }
```

### MapperPlugin

Maps extracted fields to a target schema.

```python
from pdf_autofillr_plugins.interfaces import MapperPlugin, PluginMetadata

@plugin(category="mapper", name="my-mapper")
class MyMapper(MapperPlugin):

    def get_metadata(self) -> PluginMetadata: ...

    def supports_schema(self, schema: dict) -> bool:
        """Return True if this mapper can handle the schema."""
        return True

    def map_fields(self, extracted_fields: list, target_schema=None, **kwargs) -> dict:
        """Map fields to target schema. Return mapped_fields, unmapped_fields."""
        mapped = {f["name"]: f["value"] for f in extracted_fields if f["name"] in (target_schema or {})}
        unmapped = [f["name"] for f in extracted_fields if f["name"] not in (target_schema or {})]
        return {
            "mapped_fields": mapped,
            "unmapped_fields": unmapped,
            "mapping_info": [],
            "mapper": "my-mapper",
            "confidence": 1.0,
            "coverage": len(mapped) / len(extracted_fields) if extracted_fields else 0.0,
        }
```

### ValidatorPlugin

Validates a field value and returns errors and warnings.

```python
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(category="validator", name="my-validator")
class MyValidator(ValidatorPlugin):

    def get_metadata(self) -> PluginMetadata: ...

    def supports_field_type(self, field_type: str) -> bool:
        return field_type.lower() in {"my_type"}

    def validate(self, field_name, field_value, rules=None, **kwargs) -> dict:
        errors = []
        warnings = []
        # ... validation logic ...
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validator": "my-validator",
            "field_name": field_name,
            "field_value": field_value,
        }
```

### FillerPlugin

Fills a PDF template with data.

```python
from pdf_autofillr_plugins.interfaces import FillerPlugin, PluginMetadata

@plugin(category="filler", name="my-filler")
class MyFiller(FillerPlugin):

    def get_metadata(self) -> PluginMetadata: ...

    def supports_pdf_type(self, pdf_path: str) -> bool:
        return True

    def fill(self, pdf_path: str, data: dict, output_path=None, **kwargs) -> dict:
        out = output_path or pdf_path.replace(".pdf", "_filled.pdf")
        # ... your filling logic ...
        return {
            "output_path": out,
            "filled_fields": list(data.keys()),
            "unfilled_fields": [],
            "filler": "my-filler",
        }
```

### ChunkerPlugin, EmbedderPlugin, TransformerPlugin

See interface files in `src/pdf_autofillr_plugins/interfaces/` — same pattern.

---

## 5. The @plugin decorator

```python
@plugin(
    category="validator",       # required
    name="phone-validator",     # optional — defaults to class name
    version="1.0.0",            # optional — default "1.0.0"
    author="Your Team",         # optional
    description="...",          # optional — falls back to class docstring
    tags=["phone", "kyc"],      # optional — list of strings, used for filtering
    priority=150,               # optional — default 100; higher = loaded first by find_*
    enabled=True,               # optional — set False to disable without deleting
    config_schema={},           # optional — JSON schema for config validation
)
```

The decorator attaches metadata as class attributes (`_plugin_name`, `_plugin_category`, etc.) and sets `_is_plugin = True` so the registry can identify it.

### @requires

Declare pip dependencies for your plugin:

```python
from pdf_autofillr_plugins.decorators import requires

@plugin(category="extractor", name="ml-extractor")
@requires("numpy>=1.24", "scikit-learn>=1.3")
class MLExtractor(ExtractorPlugin):
    ...
```

---

## 6. PluginRegistry

Low-level class. Usually accessed via `PluginManager.registry`.

```python
from pdf_autofillr_plugins import PluginRegistry

registry = PluginRegistry()

# Manual registration
registry.register_plugin(MyValidator, category="validator", name="my-validator")

# Auto-discovery — file system directory
registry.discover_plugins(["./my_plugins/"])

# Auto-discovery — installed Python module
registry.discover_plugins(["my_company.pdf_plugins"])

# Auto-discovery — multiple paths, filter by category
registry.discover_plugins(
    ["./plugins/", "my_company.plugins"],
    categories=["validator", "extractor"],
)

# Look up a class
cls = registry.get_plugin_class("my-validator", category="validator")
cls = registry.get_plugin_class("my-validator")  # searches all categories

# List registered plugins
all_plugins = registry.list_plugins()           # {"validator": [...], ...}
validators  = registry.list_plugins("validator")# {"validator": [...]}

# Get metadata without instantiating
info = registry.get_plugin_info("my-validator", "validator")

# Clear all
registry.clear()
```

---

## 7. PluginManager

High-level interface. Use this in application code.

```python
from pdf_autofillr_plugins import PluginManager

manager = PluginManager(
    plugin_paths=["./my_plugins/"],  # discovers plugins at init time
    enabled_plugins=["email-validator", "my-validator"],  # allowlist; None = all
    lazy_load=True,  # default — plugins load on first use
)

# Load a plugin by name and category
plugin = manager.load_plugin("my-validator", "validator")
plugin = manager.load_plugin("my-validator", "validator", config={"key": "value"})

# Load same plugin twice — returns cached instance
p1 = manager.load_plugin("my-validator", "validator")
p2 = manager.load_plugin("my-validator", "validator")
assert p1 is p2  # True

# Get a plugin (loads lazily)
plugin = manager.get_plugin("my-validator", "validator")

# Auto-select best extractor for a file (uses supports())
extractor = manager.find_extractor("invoice.pdf", some_context="value")

# Auto-select best mapper for a schema (uses supports_schema())
mapper = manager.find_mapper({"investor_name": "str", "email": "str"})

# List all plugins
all_plugins = manager.list_plugins()
validators  = manager.list_plugins("validator")

# Get plugin metadata without loading
info = manager.get_plugin_info("email-validator", "validator")

# Unload one plugin
manager.unload_plugin("my-validator", "validator")

# Shutdown all — calls shutdown() on each loaded plugin
manager.shutdown()
```

---

## 8. Built-in plugins

### EmailValidatorPlugin

```python
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
```

Validates:
- String type check
- RFC-5321 format (regex)
- Max 254 characters
- Warns on disposable domains (tempmail.com, mailinator.com, etc.)

Optional rules dict:

| Rule | Type | Effect |
|---|---|---|
| `require_corporate` | `bool` | Warns on gmail.com, yahoo.com, hotmail.com |
| `allowed_domains` | `list[str]` | Errors if domain not in list |

Supported field types: `email`, `email_address`, `emailaddress`, `e-mail`

```python
v = EmailValidatorPlugin()
v.initialize()

v.validate("email", "user@example.com")
# {"valid": True, "errors": [], "warnings": []}

v.validate("email", "user@gmail.com", rules={"allowed_domains": ["company.com"]})
# {"valid": False, "errors": ["Email domain not in allowed list: gmail.com"]}
```

### PassthroughExtractorPlugin

```python
from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import PassthroughExtractorPlugin
```

Returns pre-configured fields unchanged. `supports()` returns `True` only when `config["fields"]` is set.

```python
e = PassthroughExtractorPlugin(config={"fields": [
    {"name": "investor_name", "value": "Jane", "confidence": 0.99},
]})
e.initialize()
result = e.extract("form.pdf")
# {"fields": [...], "extractor": "passthrough-extractor", "confidence": 1.0}
```

### IdentityMapperPlugin

```python
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
```

Mapping strategy (in order):
1. Exact field name match against schema keys
2. Snake-case normalised match (`"Investor Name"` → `investor_name`)
3. Passthrough when no schema is provided
4. Mark as unmapped

```python
m = IdentityMapperPlugin()
m.initialize()
result = m.map_fields(
    [{"name": "Investor Name", "value": "Jane", "confidence": 1.0}],
    target_schema={"investor_name": "string"},
)
# {"mapped_fields": {"investor_name": "Jane"}, "unmapped_fields": [], "coverage": 1.0}
```

---

## 9. Examples

See the `examples/` directory:

- `examples/custom_validator.py` — phone number validator with E.164 format
- `examples/custom_extractor.py` — invoice PDF extractor with priority override

Run them:

```bash
python examples/custom_validator.py
python examples/custom_extractor.py
```

---

## 10. Integration with pdf-autofillr modules

### With the chatbot module

```python
from chatbot import chatbotClient
from pdf_autofillr_plugins import PluginManager

# Discover your plugins
manager = PluginManager(plugin_paths=["./my_plugins/"])

# Validate collected fields before filling
chatbot = chatbotClient.from_env()
session = chatbot.create_session(pdf_path="blank.pdf", user_id="u1")

# After session completes, validate the data
collected_data = session.collected_data
validator = manager.load_plugin("email-validator", "validator")
for field_name, value in collected_data.items():
    result = validator.validate(field_name, value)
    if not result["valid"]:
        print(f"  ✗ {field_name}: {result['errors']}")
```

### With the mapper module

```python
from pdf_autofillr_mapper import MapperOrchestrator
from pdf_autofillr_plugins import PluginManager

# Use a custom extractor plugin before mapper fills the PDF
manager = PluginManager(plugin_paths=["./my_plugins/"])
extractor = manager.find_extractor("my_invoice.pdf")
if extractor:
    raw = extractor.extract("my_invoice.pdf")
    # Pass extracted fields to mapper
    orch = MapperOrchestrator.from_env()
    orch.fill_pdf(pdf_path="blank.pdf", user_id="u1", pdf_doc_id="lp_v1",
                  user_data={f["name"]: f["value"] for f in raw["fields"]})
```

### Via the CLI

```bash
# List your plugins
pdf-autofillr plugins list --path ./my_plugins/

# Get info on a specific plugin
pdf-autofillr plugins info phone-validator
```

---

## 11. Testing your plugins

The `passthrough-extractor` and `noop` patterns make unit testing plugins straightforward:

```python
import pytest
from my_plugins.phone_validator import PhoneValidatorPlugin

@pytest.fixture
def validator():
    v = PhoneValidatorPlugin()
    v.initialize()
    return v

def test_valid_e164(validator):
    result = validator.validate("phone", "+12125551234")
    assert result["valid"] is True

def test_invalid_format(validator):
    result = validator.validate("phone", "555-1234")
    assert result["valid"] is False
    assert len(result["errors"]) > 0

def test_supports_phone_type(validator):
    assert validator.supports_field_type("phone") is True
    assert validator.supports_field_type("email") is False
```

Test discovery from a temp directory:

```python
def test_discovery(tmp_path):
    (tmp_path / "my_plugin.py").write_text("""
from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces.validator_plugin import ValidatorPlugin
from pdf_autofillr_plugins.interfaces.base_plugin import PluginMetadata

@plugin(category="validator", name="test-plugin")
class TestPlugin(ValidatorPlugin):
    def get_metadata(self):
        return PluginMetadata(name="test-plugin", version="1.0", author="T",
                              description="", category="validator")
    def validate(self, name, value, rules=None, **kw):
        return {"valid": True, "errors": [], "warnings": [], "validator": "test-plugin"}
    def supports_field_type(self, ft): return True
""")
    from pdf_autofillr_plugins import PluginManager
    manager = PluginManager()
    discovered = manager.discover_plugins([str(tmp_path)])
    assert "test-plugin" in discovered.get("validator", [])
```

---

## 12. Troubleshooting

**Plugin not discovered**

Make sure:
1. The class is decorated with `@plugin`
2. It inherits from the correct interface (e.g. `ValidatorPlugin`)
3. The file does not start with `_`
4. The search path points to the directory containing the `.py` file, not the file itself

**`load_plugin` returns `None`**

Either the plugin name/category doesn't match what's registered, or the plugin is in the `enabled_plugins` allowlist check. Call `manager.list_plugins()` to see what's actually registered.

**`initialize()` not called**

`PluginManager.load_plugin()` always calls `initialize()` automatically. If you're using `PluginRegistry` directly and instantiating classes yourself, you need to call `instance.initialize()` manually.

**Priority not respected by `find_extractor`**

`find_extractor` sorts by priority descending — higher priority wins. Make sure your plugin's `supports()` method returns `True` for the file being tested.
