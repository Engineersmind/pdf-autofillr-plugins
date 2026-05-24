[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pdf-autofillr-plugins)](https://pypi.org/project/pdf-autofillr-plugins/)
[![Python](https://img.shields.io/pypi/pyversions/pdf-autofillr-plugins)](https://pypi.org/project/pdf-autofillr-plugins/)
[![Tests](https://github.com/Engineersmind/pdf-autofillr-plugins/actions/workflows/tests.yml/badge.svg)](https://github.com/Engineersmind/pdf-autofillr-plugins/actions/workflows/tests.yml)
[![Platform](https://img.shields.io/badge/platform-pdffillr.ai-blue)](https://pdffillr.ai)

<div align="center">

# pdf-autofillr Plugins

**Extend pdf-autofillr with custom LLM providers, field extractors, and data transformers.**

[**Quick Start**](#quick-start) · [**Python SDK**](https://github.com/EngineersMind/pdf-autofillr-python-sdk) · [**Live Platform**](https://pdffillr.ai) · [**USAGE.md**](plugins/USAGE.md)

</div>

---

> **Status:** Plugin architecture is under active design. This repository tracks the plugin specification, issue backlog, and community plugin index. The base classes and registry live in [pdf-autofillr-python-sdk](https://github.com/EngineersMind/pdf-autofillr-python-sdk) and are published separately as `pdf-autofillr-plugins`.

## What are plugins?

Plugins let you customize the pdf-autofillr pipeline:

| Plugin type | What it customizes | Status |
|-------------|-------------------|--------|
| **LLM adapter** | Use any LLM (local, fine-tuned, or proprietary) for field mapping | ✅ Available |
| **Extractor** | Custom PDF parsing logic for non-standard form types | ✅ Available |
| **Mapper** | Custom field-to-schema mapping strategy | ✅ Available |
| **Validator** | Custom field validation rules (email, phone, date, allowlists) | ✅ Available |
| **Transformer** | Pre/post-process data (formatting, validation, enrichment) | ✅ Available |
| **Filler** | Custom PDF filling strategy | ✅ Available |
| **Chunker** | Custom PDF chunking for large documents | ✅ Available |
| **Embedder** | Custom metadata embedding format | ✅ Available |
| **Output formatter** | Control output format (annotated PDF, JSON report, audit trail) | ✅ Available |
| **Data connector** | Pull fill data from CRMs, databases, or APIs | ✅ Available |

## Quick Start

```bash
pip install pdf-autofillr-plugins
pdf-autofillr-plugins setup    # copies .env and usage/ guides
pdf-autofillr-plugins status   # verify installation
```

### Write your first plugin

```python
from pdf_autofillr_plugins import plugin, PluginManager
from pdf_autofillr_plugins.interfaces import LLMAdapter, PluginMetadata

@plugin(category="llm_adapter", name="my-custom-llm")
class MyCustomLLM(LLMAdapter):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-custom-llm", version="1.0.0",
            author="Your Team", description="My custom LLM",
            category="llm_adapter",
        )

    def map_fields(self, fields: list[str], context: str) -> dict:
        # Your custom mapping logic
        return {field: self.call_my_llm(field, context) for field in fields}

    def embed(self, fields: list[str], schema_keys: list[str]) -> dict:
        return {field: {"schema_key": schema_keys[i], "confidence": 0.9}
                for i, field in enumerate(fields)}
```

Then use it:

```python
manager = PluginManager()
manager.registry.register_plugin(MyCustomLLM, "llm_adapter", "my-custom-llm")

llm = manager.load_plugin("my-custom-llm", "llm_adapter")
mapping = llm.map_fields(
    fields=["investor_full_name", "commitment_amount_usd"],
    context="LP Subscription Agreement",
)
# {"investor_full_name": ..., "commitment_amount_usd": ...}
```

> Full base class API is documented in [plugins/USAGE.md](plugins/USAGE.md).

## Built-in Plugins

Ready to use out of the box:

| Plugin | Category | Description |
|--------|----------|-------------|
| `noop-llm` | llm_adapter | Passthrough LLM — exact name match. No API calls. For testing. |
| `litellm` | llm_adapter | Production adapter — OpenAI, Anthropic, Ollama, Gemini, Groq, Bedrock |
| `email-validator` | validator | Email format, length, disposable domain, allowed domain rules |
| `passthrough-extractor` | extractor | Returns pre-configured fields unchanged — for testing |
| `invoice-extractor` | extractor | Extracts invoice_number, invoice_date, vendor_name, total_amount |
| `identity-mapper` | mapper | Exact + snake_case normalised field-to-schema mapping |
| `ml-mapper` | mapper | Synonym-table mapper with 25+ built-in mappings |
| `json-report` | output_formatter | Wraps filled PDF in JSON report with field coverage and audit trail |
| `passthrough-formatter` | output_formatter | Returns raw PDF bytes unchanged (default) |
| `dict-connector` | data_connector | In-memory dict connector — for testing |
| `json-file-connector` | data_connector | Loads fill data from a JSON file keyed by record_id |

## Official Plugins (Planned)

| Plugin | Description | Status |
|--------|-------------|--------|
| `pdf-autofillr-plugin-openai` | OpenAI GPT-4o/4o-mini adapter | Planned |
| `pdf-autofillr-plugin-anthropic` | Anthropic Claude adapter | Planned |
| `pdf-autofillr-plugin-ollama` | Local Ollama models | Planned |
| `pdf-autofillr-plugin-google` | Google Gemini adapter | Planned |
| Community plugins | Custom extractors, connectors | [Contribute yours!](#contributing) |

## Plugin Types

### LLM Adapter

Implement `LLMAdapter` to add support for any LLM — local, fine-tuned, or proprietary:

```python
from pdf_autofillr_plugins.interfaces import LLMAdapter, PluginMetadata

class MyLLMAdapter(LLMAdapter):
    name = "my-llm"

    def get_metadata(self) -> PluginMetadata: ...

    def map_fields(self, fields: list[str], context: str) -> dict:
        # Call your LLM and return field_name → schema_key mapping
        return {field: self.call_my_api(field, context) for field in fields}

    def embed(self, fields: list[str], schema_keys: list[str]) -> dict:
        # Return embedding metadata baked into the PDF template
        return {field: {"schema_key": schema_keys[i], "confidence": 0.9}
                for i, field in enumerate(fields)}
```

### Extractor Plugin

Customize PDF field extraction:

```python
from pdf_autofillr_plugins.interfaces import ExtractorPlugin, PluginMetadata

class MyExtractor(ExtractorPlugin):
    name = "my-extractor"

    def get_metadata(self) -> PluginMetadata: ...

    def supports(self, pdf_path: str, **kwargs) -> bool:
        return "contract" in pdf_path.lower()

    def extract(self, pdf_path: str, strategy=None, **kwargs) -> dict:
        fields = [{"name": "party_name", "value": "Acme Corp", "confidence": 0.95}]
        return {"fields": fields, "metadata": {}, "extractor": "my-extractor"}
```

### Transformer Plugin

Pre- or post-process fill data:

```python
from pdf_autofillr_plugins.interfaces import TransformerPlugin, PluginMetadata

class DateNormalizer(TransformerPlugin):
    name = "date-normalizer"

    def get_metadata(self) -> PluginMetadata: ...

    def supports_type(self, value_type: type) -> bool:
        return value_type in {str}

    def transform(self, value, transform_type=None, **kwargs):
        # Normalize all date fields to ISO 8601
        from datetime import datetime
        for fmt in ("%m/%d/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(str(value), fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return value
```

### Output Formatter

Control how filled PDFs and metadata are returned:

```python
from pdf_autofillr_plugins.interfaces import OutputFormatterPlugin, PluginMetadata

class JSONReportFormatter(OutputFormatterPlugin):
    name = "json-report"

    def get_metadata(self) -> PluginMetadata: ...

    def format(self, filled_pdf: bytes, field_map: dict, **kwargs) -> dict:
        return {"pdf": filled_pdf, "report": field_map, "status": "ok"}
```

### Data Connector

Pull fill data from external sources at fill time:

```python
from pdf_autofillr_plugins.interfaces import DataConnectorPlugin, PluginMetadata

class SalesforceConnector(DataConnectorPlugin):
    name = "salesforce"

    def get_metadata(self) -> PluginMetadata: ...

    def fetch(self, record_id: str, **kwargs) -> dict:
        # Pull contact data from Salesforce
        return {"investor_name": "Jane Smith", "email": "jane@example.com"}
```

## Packages

| Package | PyPI | Version |
|---------|------|---------|
| **pdf-autofillr-plugins** | `pip install pdf-autofillr-plugins` | 0.2.0 |

## Repository Layout

```
pdf-autofillr-plugins/
├── plugins/                ← The PyPI package (source of truth)
│   ├── src/pdf_autofillr_plugins/
│   │   ├── interfaces/     ← 10 abstract plugin interfaces
│   │   │   ├── llm_adapter.py        ← flagship — custom LLM providers
│   │   │   ├── extractor_plugin.py
│   │   │   ├── mapper_plugin.py
│   │   │   ├── validator_plugin.py
│   │   │   ├── transformer_plugin.py
│   │   │   ├── filler_plugin.py
│   │   │   ├── chunker_plugin.py
│   │   │   ├── embedder_plugin.py
│   │   │   ├── output_formatter.py   ← JSON reports, audit trails
│   │   │   └── data_connector.py     ← CRMs, databases, APIs
│   │   ├── builtin/        ← 11 ready-to-use built-in plugins
│   │   │   ├── llm_adapters/     ← NoOpLLMAdapter, LiteLLMAdapter
│   │   │   ├── extractors/       ← PassthroughExtractor, InvoiceExtractor
│   │   │   ├── mappers/          ← IdentityMapper, MLMapper
│   │   │   ├── validators/       ← EmailValidator
│   │   │   ├── output_formatters/← JSONReportFormatter, PassthroughFormatter
│   │   │   └── data_connectors/  ← DictConnector, JSONFileConnector
│   │   ├── registry.py     ← PluginRegistry (discover + register)
│   │   ├── manager.py      ← PluginManager (load + find + cache + run)
│   │   └── decorators.py   ← @plugin, @requires
│   ├── tests/              ← 221 tests (unit + integration)
│   ├── examples/           ← Working plugin examples
│   └── usage/              ← Per-plugin-type usage guides
├── benchmarks/             ← Plugin performance suite (6 domains)
├── deployment/             ← Docker configs
├── docs/                   ← Architecture and guides
└── examples/               ← Top-level usage examples
```

## Development

```bash
git clone https://github.com/Engineersmind/pdf-autofillr-plugins.git
cd pdf-autofillr-plugins/plugins
pip install -e ".[dev]"
pytest tests/ -v    # 221 tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide.

## Contributing

1. Open an [issue](https://github.com/Engineersmind/pdf-autofillr-plugins/issues) describing your plugin idea
2. Fork this repository
3. Implement your plugin by extending the appropriate base class from `pdf_autofillr_plugins.interfaces`
4. Add tests alongside your implementation — all 221 existing tests must still pass
5. Submit a pull request following the [branch and commit conventions](CONTRIBUTING.md)

## Related

| Package | Description |
|---------|-------------|
| [pdf-autofillr-python-sdk](https://github.com/EngineersMind/pdf-autofillr-python-sdk) | Python library for programmatic use |
| [pdf-autofillr-cli](https://github.com/EngineersMind/pdf-autofillr-cli) | Command-line interface |
| [pdffillr.ai](https://pdffillr.ai) | Live platform |

## License

MIT — see [LICENSE](LICENSE).
