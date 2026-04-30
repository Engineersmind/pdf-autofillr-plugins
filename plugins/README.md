# pdf-autofillr-plugins

> Plugin framework for extending pdf-autofillr — zero runtime dependencies, pure Python.

Build custom extractors, mappers, validators, fillers, chunkers, embedders, and transformers and drop them into any pdf-autofillr module without touching its source code.

```bash
pip install pdf-autofillr-plugins
```

---

## Why plugins?

pdf-autofillr ships with sensible defaults for every stage of the PDF pipeline. Plugins let you override any stage for your use case:

| Need | Plugin type |
|---|---|
| Parse a proprietary document format | `ExtractorPlugin` |
| Map fields to your internal schema | `MapperPlugin` |
| Validate phone, tax ID, IBAN fields | `ValidatorPlugin` |
| Use a custom PDF writing library | `FillerPlugin` |
| Split PDFs into domain-specific chunks | `ChunkerPlugin` |
| Use your own embedding model or provider | `EmbedderPlugin` |
| Normalise currencies, dates, addresses | `TransformerPlugin` |

---

## Install

```bash
pip install pdf-autofillr-plugins
```

No extra dependencies. The package is pure Python and works on Python 3.9+.

---

## Quick start

```python
import re
from pdf_autofillr_plugins import plugin, PluginManager
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(category="validator", name="phone-validator", version="1.0.0")
class PhoneValidatorPlugin(ValidatorPlugin):

    _E164 = re.compile(r"^\+[1-9]\d{6,14}$")

    def get_metadata(self):
        return PluginMetadata(name="phone-validator", version="1.0.0",
                              author="You", description="E.164 phone validator",
                              category="validator")

    def supports_field_type(self, field_type):
        return field_type.lower() in {"phone", "telephone", "mobile"}

    def validate(self, field_name, field_value, rules=None, **kwargs):
        errors = [] if self._E164.match(str(field_value)) else [f"Invalid: {field_value!r}"]
        return {"valid": not errors, "errors": errors, "warnings": [], "validator": "phone-validator"}

# Register and use
manager = PluginManager()
manager.registry.register_plugin(PhoneValidatorPlugin, "validator", "phone-validator")

validator = manager.load_plugin("phone-validator", "validator")
print(validator.validate("phone", "+12125551234"))
# {"valid": True, "errors": [], "warnings": [], "validator": "phone-validator"}
```

→ See [quickstart.md](quickstart.md) for more examples.

---

## Plugin interfaces

| Interface | Method to implement | Use for |
|---|---|---|
| `ExtractorPlugin` | `extract()`, `supports()` | Reading data from PDFs or documents |
| `MapperPlugin` | `map_fields()`, `supports_schema()` | Mapping fields to a target schema |
| `ValidatorPlugin` | `validate()`, `supports_field_type()` | Validating field values |
| `FillerPlugin` | `fill()`, `supports_pdf_type()` | Writing data into PDFs |
| `ChunkerPlugin` | `chunk()` | Splitting PDF content for processing |
| `EmbedderPlugin` | `embed()`, `check()` | Embedding metadata into PDFs |
| `TransformerPlugin` | `transform()`, `supports_type()` | Transforming field values |

All interfaces extend `BasePlugin` which provides: `initialize()`, `shutdown()`, `config`, `name`, `version`, `category`, `is_initialized`.

---

## Built-in plugins

Three plugins ship with the package and are ready to use:

### `email-validator` (category: `validator`)

Validates email addresses: format, length, disposable domain detection, and optional rules.

```python
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
from pdf_autofillr_plugins import PluginManager

manager = PluginManager()
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
v = manager.load_plugin("email-validator", "validator")

v.validate("email", "user@example.com")
# {"valid": True,  "errors": [], "warnings": []}

v.validate("email", "test@tempmail.com")
# {"valid": True, "errors": [], "warnings": ["Disposable email domain detected: tempmail.com"]}

v.validate("email", "not-an-email")
# {"valid": False, "errors": ["Invalid email format: 'not-an-email'"]}

# Custom rules
v.validate("email", "user@gmail.com", rules={"allowed_domains": ["company.com"]})
# {"valid": False, "errors": ["Email domain not in allowed list: gmail.com"]}
```

### `passthrough-extractor` (category: `extractor`)

Returns pre-configured fields unchanged. Useful for testing pipelines without a real PDF.

```python
from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import PassthroughExtractorPlugin

fields = [
    {"name": "investor_name", "value": "Jane Smith", "confidence": 0.99},
    {"name": "email", "value": "jane@example.com", "confidence": 0.98},
]
extractor = PassthroughExtractorPlugin(config={"fields": fields})
extractor.initialize()

result = extractor.extract("blank_form.pdf")
# {"fields": [...], "extractor": "passthrough-extractor", "confidence": 1.0}
```

### `identity-mapper` (category: `mapper`)

Maps extracted fields to a schema by exact match, then snake_case normalisation.

```python
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin

mapper = IdentityMapperPlugin()
mapper.initialize()

result = mapper.map_fields(
    extracted_fields=[
        {"name": "Investor Name", "value": "Jane Smith", "confidence": 1.0},
        {"name": "email_address", "value": "jane@example.com", "confidence": 1.0},
    ],
    target_schema={
        "investor_name": "string",
        "email_address": "string",
    },
)
# {
#   "mapped_fields": {"investor_name": "Jane Smith", "email_address": "jane@example.com"},
#   "unmapped_fields": [],
#   "coverage": 1.0,
# }
```

---

## The `@plugin` decorator

```python
@plugin(
    category="extractor",       # required — extractor | mapper | validator | filler | chunker | embedder | transformer
    name="my-extractor",        # optional — defaults to class name
    version="1.0.0",            # optional — default "1.0.0"
    author="Your Team",         # optional
    description="What it does", # optional
    tags=["invoice", "finance"],# optional — for filtering
    priority=200,               # optional — higher loads first (default 100)
    enabled=True,               # optional — can be disabled without removing
)
class MyExtractor(ExtractorPlugin):
    ...
```

---

## Plugin discovery

The registry can discover plugins automatically from a directory or a module path:

```python
manager = PluginManager()

# From a file system directory — scans all .py files
manager.discover_plugins(["./my_plugins/", "./team_plugins/"])

# From an installed Python module
manager.discover_plugins(["my_company.pdf_plugins"])

# Filter by category
manager.discover_plugins(["./my_plugins/"], categories=["validator"])
```

---

## PluginManager API

```python
from pdf_autofillr_plugins import PluginManager

manager = PluginManager(
    plugin_paths=["./my_plugins/"],  # auto-discover on init
    enabled_plugins=["email-validator", "phone-validator"],  # allowlist (None = all)
    lazy_load=True,  # load on-demand vs at startup
)

# Register manually
manager.registry.register_plugin(MyValidator, "validator", "my-validator")

# Load a plugin (returns None if not found or not enabled)
validator = manager.load_plugin("my-validator", "validator")

# Get a loaded plugin (loads lazily if not yet loaded)
plugin = manager.get_plugin("my-validator", "validator")

# Auto-select the best extractor for a file (uses supports())
extractor = manager.find_extractor("path/to/invoice.pdf")

# Auto-select the best mapper for a schema (uses supports_schema())
mapper = manager.find_mapper({"investor_name": "str", "email": "str"})

# List all registered plugins
all_plugins = manager.list_plugins()             # {"validator": [...], "extractor": [...]}
validators   = manager.list_plugins("validator") # {"validator": [...]}

# Metadata without loading the plugin
info = manager.get_plugin_info("email-validator", "validator")
# {"name": "email-validator", "version": "1.0.0", "author": "...", "priority": 100, ...}

# Unload a single plugin
manager.unload_plugin("email-validator", "validator")

# Shutdown all — calls shutdown() on each loaded plugin
manager.shutdown()
```

---

## For developers

### Run from source

```bash
git clone https://github.com/Engineersmind/pdf-autofillr.git
cd pdf-autofillr/packages/plugins

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Project layout

```
packages/plugins/
├── src/
│   └── pdf_autofillr_plugins/
│       ├── __init__.py              # public API — PluginManager, PluginRegistry, @plugin
│       ├── manager.py               # PluginManager
│       ├── registry.py              # PluginRegistry
│       ├── decorators.py            # @plugin, @requires
│       ├── interfaces/
│       │   ├── __init__.py          # re-exports all interfaces
│       │   ├── base_plugin.py       # BasePlugin, PluginMetadata
│       │   ├── extractor_plugin.py
│       │   ├── mapper_plugin.py
│       │   ├── validator_plugin.py
│       │   ├── filler_plugin.py
│       │   ├── chunker_plugin.py
│       │   ├── embedder_plugin.py
│       │   └── transformer_plugin.py
│       └── builtin/
│           ├── validators/
│           │   └── email_validator.py
│           ├── extractors/
│           │   └── passthrough_extractor.py
│           └── mappers/
│               └── identity_mapper.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_builtin_plugins.py
│   │   └── test_registry_and_manager.py
│   └── integration/
│       └── test_plugin_lifecycle.py
├── examples/
│   ├── custom_validator.py
│   └── custom_extractor.py
├── requirements/
│   ├── base.txt
│   └── dev.txt
├── .env.example
├── CHANGELOG.md
├── LICENSE
├── MANIFEST.in
├── README.md
├── USAGE.md
├── quickstart.md
└── pyproject.toml
```

### Run tests

```bash
pip install -e ".[dev]"

# All tests (64 tests, ~0.5s, no external deps)
pytest tests/ -v

# Unit only
pytest tests/unit/ -v

# Integration only
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src/pdf_autofillr_plugins --cov-report=term-missing
```

### Publish a new version

```bash
# 1. Bump version in pyproject.toml and src/pdf_autofillr_plugins/__init__.py
# 2. Add entry to CHANGELOG.md
# 3. Build
pip install build
python -m build
# 4. Upload
pip install twine
twine upload dist/*
```

---

## License

MIT — see [LICENSE](LICENSE).
