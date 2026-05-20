[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-pdffillr.ai-blue)](https://pdffillr.ai)

<div align="center">

# pdf-autofillr Plugins

**Extend pdf-autofillr with custom LLM providers, field extractors, and data transformers.**

[**Quick Start**](#quick-start) · [**Python SDK**](https://github.com/EngineersMind/pdf-autofillr-python-sdk) · [**Live Platform**](https://pdffillr.ai)

</div>

---

> **Status:** Plugin architecture is under active design. This repository tracks the plugin specification, issue backlog, and community plugin index. The base classes and registry live in [pdf-autofillr-python-sdk](https://github.com/EngineersMind/pdf-autofillr-python-sdk).

## What are plugins?

Plugins let you customize the pdf-autofillr pipeline:

| Plugin type | What it customizes | Status |
|-------------|-------------------|--------|
| **LLM adapter** | Use any LLM (local, fine-tuned, or proprietary) for field mapping | Planned |
| **Extractor** | Custom PDF parsing logic for non-standard form types | Planned |
| **Transformer** | Pre/post-process data (formatting, validation, enrichment) | Planned |
| **Output formatter** | Control output format (annotated PDF, JSON report, audit trail) | Planned |
| **Data connector** | Pull fill data from CRMs, databases, or APIs | Planned |

## Quick Start

Plugins are imported from the [Python SDK](https://github.com/EngineersMind/pdf-autofillr-python-sdk). Install it first:

```bash
pip install pdf-autofillr
```

Then implement a custom plugin:

```python
from pdf_autofillr.plugins import register_plugin
from pdf_autofillr.plugins.base import LLMAdapter

class MyCustomLLM(LLMAdapter):
    def map_fields(self, fields: list[str], context: str) -> dict:
        # Your custom mapping logic
        return {field: self.call_my_llm(field, context) for field in fields}

register_plugin("my-custom-llm", MyCustomLLM)
```

Then use it:

```python
from pdf_autofillr import PDFAutofillr

client = PDFAutofillr(llm_adapter="my-custom-llm")
```

> Full base class API is documented in the [Python SDK repo](https://github.com/EngineersMind/pdf-autofillr-python-sdk/tree/main/plugins).

## Plugin Types

### LLM Adapter

Implement `LLMAdapter` to add support for any LLM:

```python
from pdf_autofillr.plugins.base import LLMAdapter

class MyLLMAdapter(LLMAdapter):
    name = "my-llm"

    def map_fields(self, fields, context) -> dict: ...
    def embed(self, fields, schema_keys) -> dict: ...
```

### Extractor Plugin

Customize PDF field extraction:

```python
from pdf_autofillr.plugins.base import ExtractorPlugin

class MyExtractor(ExtractorPlugin):
    name = "my-extractor"

    def extract(self, pdf_bytes: bytes) -> list[dict]: ...
```

### Transformer Plugin

Pre- or post-process fill data:

```python
from pdf_autofillr.plugins.base import TransformerPlugin

class DateNormalizer(TransformerPlugin):
    name = "date-normalizer"

    def transform(self, data: dict) -> dict:
        # Normalize all date fields to ISO 8601
        ...
```

### Output Formatter

Control how filled PDFs and metadata are returned:

```python
from pdf_autofillr.plugins.base import OutputFormatterPlugin

class JSONReportFormatter(OutputFormatterPlugin):
    name = "json-report"

    def format(self, filled_pdf: bytes, field_map: dict) -> dict:
        return {"pdf": filled_pdf, "report": field_map, "status": "ok"}
```

### Data Connector

Pull fill data from external sources at fill time:

```python
from pdf_autofillr.plugins.base import DataConnectorPlugin

class SalesforceConnector(DataConnectorPlugin):
    name = "salesforce"

    def fetch(self, record_id: str) -> dict:
        # Pull contact data from Salesforce
        ...
```

## Official Plugins

| Plugin | Description | Status |
|--------|-------------|--------|
| `pdf-autofillr-plugin-openai` | OpenAI GPT-4o/4o-mini adapter | Planned |
| `pdf-autofillr-plugin-anthropic` | Anthropic Claude adapter | Planned |
| `pdf-autofillr-plugin-ollama` | Local Ollama models | Planned |
| `pdf-autofillr-plugin-google` | Google Gemini adapter | Planned |
| Community plugins | Custom extractors, connectors | [Contribute yours!](#contributing) |

## Contributing

1. Open an [issue](https://github.com/EngineersMind/pdf-autofillr-plugins/issues) describing your plugin idea
2. Fork the [Python SDK repo](https://github.com/EngineersMind/pdf-autofillr-python-sdk) where the base classes live
3. Implement your plugin by extending the appropriate base class
4. Add tests alongside your implementation
5. Submit a pull request to the Python SDK repo and link it here

## License

MIT — see [LICENSE](LICENSE)
