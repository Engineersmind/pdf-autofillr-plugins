# System Overview — pdf-autofillr-plugins

## Package structure

```
pdf_autofillr_plugins/
│
├── interfaces/                  10 abstract base classes
│   ├── base_plugin.py           BasePlugin + PluginMetadata
│   ├── llm_adapter.py           LLMAdapter          ← flagship (Sir's vision)
│   ├── extractor_plugin.py      ExtractorPlugin
│   ├── mapper_plugin.py         MapperPlugin
│   ├── validator_plugin.py      ValidatorPlugin
│   ├── filler_plugin.py         FillerPlugin
│   ├── chunker_plugin.py        ChunkerPlugin
│   ├── embedder_plugin.py       EmbedderPlugin
│   ├── transformer_plugin.py    TransformerPlugin
│   ├── output_formatter.py      OutputFormatterPlugin
│   └── data_connector.py        DataConnectorPlugin
│
├── builtin/                     11 ready-to-use built-in plugins
│   ├── llm_adapters/            NoOpLLMAdapter, LiteLLMAdapter
│   ├── extractors/              PassthroughExtractorPlugin, InvoiceExtractorPlugin
│   ├── mappers/                 IdentityMapperPlugin, MLMapperPlugin
│   ├── validators/              EmailValidatorPlugin
│   ├── output_formatters/       JSONReportFormatter, PassthroughFormatter
│   └── data_connectors/         DictConnector, JSONFileConnector
│
├── utils/                       common.py — hashing, JSON, retry, Timer, string helpers
│
├── core/                        cross-module abstractions
│   ├── handler_interface.py     HandlerInterface, BaseHandler, HandlerRequest, HandlerResponse
│   └── storage_interface.py     StorageInterface, StorageConfig, StorageProvider
│
├── decorators.py                @plugin, @requires, @cache_result, @pre_execute, @post_execute
├── registry.py                  PluginRegistry — discovers and stores plugin classes
├── manager.py                   PluginManager  — loads, caches, finds, and runs plugins
└── cli.py                       pdf-autofillr-plugins setup/status/list CLI
```

## Plugin lifecycle

```
Write class → @plugin decorator → PluginRegistry.register_plugin() (or auto-discover)
                                           ↓
                               PluginManager.load_plugin()
                                           ↓
                               plugin_instance.initialize()   ← set up resources once
                                           ↓
                               plugin_instance.<method>()     ← your business logic
                                           ↓
                               PluginManager.unload_plugin()
                                           ↓
                               plugin_instance.shutdown()     ← clean up resources
```

## Full pipeline — Sir's vision

```
DataConnector.fetch(record_id)
        ↓  investor data dict
LLMAdapter.map_fields(pdf_fields, context)
        ↓  field_name → schema_key mapping
LLMAdapter.embed(fields, schema_keys)
        ↓  embedding metadata baked into PDF
[mapper module fills the PDF]
        ↓  filled_pdf bytes + field_map
OutputFormatterPlugin.format(filled_pdf, field_map)
        ↓  JSON report / raw bytes / any format
```

## Plugin priority

When multiple plugins in the same category are registered, `PluginManager.find_*()` selects
the one with the **highest priority** whose `supports_*()` method returns `True`.

| Plugin | Category | Priority |
|--------|----------|----------|
| `litellm` | llm_adapter | 100 |
| `json-report` | output_formatter | 100 |
| `json-file-connector` | data_connector | 50 |
| `invoice-extractor` | extractor | 200 |
| `ml-mapper` | mapper | 150 |
| `identity-mapper` | mapper | 1 |
| `passthrough-extractor` | extractor | 1 |
| `passthrough-formatter` | output_formatter | 1 |
| `noop-llm` | llm_adapter | 1 |
| `dict-connector` | data_connector | 1 |

## PluginManager.find_* methods

```python
manager.find_llm_adapter("gpt-4o")        # → LiteLLMAdapter (supports any model, priority 100)
manager.find_llm_adapter("noop")          # → LiteLLMAdapter (also supports "noop", higher priority)
manager.find_llm_adapter("")              # → highest priority adapter
manager.find_output_formatter("json")     # → JSONReportFormatter
manager.find_output_formatter("raw")      # → PassthroughFormatter
manager.find_data_connector("dict")       # → DictConnector
manager.find_data_connector("json")       # → JSONFileConnector (priority 50 > DictConnector 1)
manager.find_extractor("invoice.pdf")     # → InvoiceExtractorPlugin (supports "invoice" in name)
manager.find_mapper(schema)               # → highest priority mapper that supports_schema()
```
