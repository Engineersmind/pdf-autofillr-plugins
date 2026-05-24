# pdf-autofillr-plugins

Plugin framework for [pdf-autofillr](https://github.com/Engineersmind/pdf-autofillr-python-sdk) — extend extractors, mappers, validators, fillers, and more.

## Install

```bash
pip install pdf-autofillr-plugins
pip install "pdf-autofillr-plugins[dev]"   # + dev tools
```

## Quick Start

```bash
pdf-autofillr-plugins setup    # copy configs/ and usage/ guides
pdf-autofillr-plugins status   # check installation
```

See [USAGE.md](USAGE.md) for the full reference and [quickstart.md](quickstart.md) for a 2-minute walkthrough.

## Built-in Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| `email-validator` | validator | Email format, length, disposable domain, allowed domain rules |
| `passthrough-extractor` | extractor | Returns pre-configured fields unchanged — for testing |
| `invoice-extractor` | extractor | Extracts invoice_number, invoice_date, vendor_name, total_amount |
| `identity-mapper` | mapper | Exact + snake_case normalised field-to-schema mapping |
| `ml-mapper` | mapper | Synonym-table mapper with 25+ built-in mappings |

## Version

**0.2.0** — see [CHANGELOG.md](CHANGELOG.md) for what changed.
