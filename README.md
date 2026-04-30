# pdf-autofillr-plugins

> Plugin framework for extending pdf-autofillr — zero runtime dependencies, pure Python.

[![PyPI](https://img.shields.io/pypi/v/pdf-autofillr-plugins)](https://pypi.org/project/pdf-autofillr-plugins/)
[![Python](https://img.shields.io/pypi/pyversions/pdf-autofillr-plugins)](https://pypi.org/project/pdf-autofillr-plugins/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/Engineersmind/pdf-autofillr-plugins/actions/workflows/tests.yml/badge.svg)](https://github.com/Engineersmind/pdf-autofillr-plugins/actions)

```bash
pip install pdf-autofillr-plugins
```

## Quick start

```python
from pdf_autofillr_plugins import plugin, PluginManager
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(category="validator", name="my-validator", version="1.0.0")
class MyValidator(ValidatorPlugin):
    def get_metadata(self): ...
    def validate(self, field_name, field_value, rules=None, **kwargs):
        return {"valid": True, "errors": [], "warnings": [], "validator": "my-validator"}
    def supports_field_type(self, ft): return True

manager = PluginManager()
manager.registry.register_plugin(MyValidator, "validator", "my-validator")
v = manager.load_plugin("my-validator", "validator")
print(v.validate("email", "test@example.com"))
```

## Built-in plugins (5 ready to use)

| Plugin | Category | Description |
|---|---|---|
| `email-validator` | validator | Email format, length, disposable domain checks |
| `passthrough-extractor` | extractor | Returns pre-configured fields — testing helper |
| `invoice-extractor` | extractor | Extracts invoice number, date, vendor, total |
| `identity-mapper` | mapper | Exact + snake_case schema mapping |
| `ml-mapper` | mapper | 25+ synonym mappings, config-extensible |

## Repository layout

```
pdf-autofillr-plugins/
├── packages/
│   └── plugins/                  ← the PyPI package (pdf-autofillr-plugins)
│       ├── src/pdf_autofillr_plugins/
│       │   ├── builtin/          ← 5 built-in plugins
│       │   ├── interfaces/       ← 8 ABC interfaces
│       │   ├── utils/            ← common helpers
│       │   └── core/             ← HandlerInterface, StorageInterface
│       ├── tests/                ← 112 tests
│       └── examples/
├── benchmarks/                   ← plugin performance benchmarks
├── deployment/                   ← Docker configs
├── docs/                         ← architecture and guides
├── examples/                     ← usage examples
└── .github/workflows/            ← CI: tests + PyPI publish
```

## Development

```bash
git clone https://github.com/Engineersmind/pdf-autofillr-plugins.git
cd pdf-autofillr-plugins/packages/plugins
pip install -e ".[dev]"
pytest tests/ -v              # 112 tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full contributor guide.

## License

MIT — see [LICENSE](LICENSE).
