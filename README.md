[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<div align="center">

# pdf-autofillr Plugins

**Extend pdf-autofillr with custom LLM providers, field extractors, output formatters, and data connectors.**

[![Platform](https://img.shields.io/badge/platform-pdffillr.ai-blue)](https://pdffillr.ai)

[**Quick Start**](#quick-start) · [**Python SDK**](https://github.com/EngineersMind/pdf-autofillr-python-sdk) · [**Live Platform**](https://pdffillr.ai)

</div>

---

> **Status:** Under active development. Official plugin registry and SDK hooks are being designed. Watch this repo for updates.

## What are plugins?

Plugins let you customize every stage of the pdf-autofillr pipeline:

| Plugin type | What it customizes |
|-------------|-------------------|
| **LLM adapter** | Use any LLM (local, fine-tuned, or proprietary) for field mapping |
| **Extractor** | Custom PDF parsing logic for non-standard form types |
| **Transformer** | Pre/post-process data before filling (formatting, validation, enrichment) |
| **Output formatter** | Control the output format (annotated PDF, JSON report, audit trail) |
| **Data connector** | Pull fill data from CRMs, databases, or APIs |

## Quick Start

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

Pre- or post-process data:

```python
from pdf_autofillr.plugins.base import TransformerPlugin

class DateNormalizer(TransformerPlugin):
    name = "date-normalizer"

    def transform(self, data: dict) -> dict:
        # Normalize all date fields to ISO 8601
        ...
```

## Official Plugins

| Plugin | Description | Status |
|--------|-------------|--------|
| `pdf-autofillr-plugin-openai` | OpenAI GPT-4o/4o-mini adapter | Built-in |
| `pdf-autofillr-plugin-anthropic` | Anthropic Claude adapter | Built-in |
| `pdf-autofillr-plugin-ollama` | Local Ollama models | Built-in |
| `pdf-autofillr-plugin-google` | Google Gemini adapter | Built-in |
| Community plugins | Custom extractors, connectors | [Contribute yours!](#contributing) |

## Contributing a Plugin

1. Fork this repo
2. Create a new directory: `plugins/<your-plugin-name>/`
3. Implement the relevant base class (see `plugins/base/`)
4. Add tests in `plugins/<your-plugin-name>/tests/`
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

## Related

| Package | Description |
|---------|-------------|
| [pdf-autofillr-python-sdk](https://github.com/EngineersMind/pdf-autofillr-python-sdk) | Core Python SDK |
| [pdf-autofillr-node-sdk](https://github.com/EngineersMind/pdf-autofillr-node-sdk) | Node.js SDK |
| [autofiller-community](https://github.com/EngineersMind/autofiller-community) | Community models and domain packs |

## License

MIT — see [LICENSE](LICENSE)
