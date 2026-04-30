# System Overview — pdf-autofillr-plugins

```
pdf_autofillr_plugins
│
├── interfaces/          8 ABCs — ExtractorPlugin, MapperPlugin, ValidatorPlugin,
│                        FillerPlugin, ChunkerPlugin, EmbedderPlugin, TransformerPlugin, BasePlugin
│
├── builtin/             5 ready-to-use plugins
│   ├── validators/      EmailValidatorPlugin
│   ├── extractors/      PassthroughExtractorPlugin, InvoiceExtractorPlugin
│   └── mappers/         IdentityMapperPlugin, MLMapperPlugin
│
├── utils/               common.py — hashing, JSON, retry, Timer, string helpers
│
├── core/                HandlerInterface, StorageInterface (cross-module abstractions)
│
├── decorators.py        @plugin, @requires
├── registry.py          PluginRegistry — discovers and stores plugin classes
└── manager.py           PluginManager  — loads, caches, and runs plugin instances
```

## Plugin lifecycle

```
@plugin decorator → PluginRegistry.register_plugin()
                         ↓
              PluginManager.load_plugin()
                         ↓
              plugin_instance.initialize()
                         ↓
              plugin_instance.<method>()   ← your business logic
                         ↓
              PluginManager.unload_plugin()
                         ↓
              plugin_instance.shutdown()
```
