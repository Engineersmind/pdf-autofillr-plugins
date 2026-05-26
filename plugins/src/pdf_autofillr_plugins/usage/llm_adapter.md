# LLMAdapter — Usage Guide

**The flagship plugin type.** Use any LLM (local, fine-tuned, or proprietary) for PDF field mapping.

## Minimum required files

```
my_plugins/
└── my_llm.py
.env                        (API key if calling a cloud LLM)
```

## Minimum .env

```bash
OPENAI_API_KEY=sk-your-key-here
# or ANTHROPIC_API_KEY, GROQ_API_KEY, etc.
```

## Write the plugin

```python
# my_plugins/my_llm.py
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import LLMAdapter, PluginMetadata

@plugin(
    category="llm_adapter",
    name="my-custom-llm",
    version="1.0.0",
    author="Your Team",
    description="Custom LLM for field mapping",
)
class MyCustomLLM(LLMAdapter):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-custom-llm", version="1.0.0",
            author="Your Team", description="My custom LLM",
            category="llm_adapter",
        )

    def map_fields(self, fields: list[str], context: str) -> dict:
        """Map each PDF field name to a canonical schema key."""
        # Your custom LLM logic here
        return {field: self.call_my_llm(field, context) for field in fields}

    def call_my_llm(self, field: str, context: str) -> str:
        """Call your LLM API and return the canonical schema key."""
        # Replace with real API call
        return field.lower().replace(" ", "_")

    def embed(self, fields: list[str], schema_keys: list[str]) -> dict:
        """Produce embedding metadata baked into the PDF template."""
        mapping = self.map_fields(fields, "")
        return {
            field: {"schema_key": mapping[field], "confidence": 0.9, "field_type": "text"}
            for field in fields
        }
```

## Use it

```python
from pdf_autofillr_plugins import PluginManager

manager = PluginManager()
manager.discover_plugins(["my_plugins/"])

llm = manager.load_plugin("my-custom-llm", "llm_adapter")
result = llm.map_fields(
    fields=["investor_full_name", "commitment_amount_usd"],
    context="LP Subscription Agreement — investor onboarding",
)
print(result)
# {"investor_full_name": "investor_full_name", "commitment_amount_usd": "commitment_amount_usd"}
```

## Use the built-in LiteLLM adapter (production)

```python
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.llm_adapters.litellm_adapter import LiteLLMAdapter

manager = PluginManager()
manager.registry.register_plugin(LiteLLMAdapter, "llm_adapter", "litellm")

llm = manager.load_plugin("litellm", "llm_adapter", config={
    "model": "openai/gpt-4o-mini",
    "api_key": "sk-...",
})

mapping = llm.map_fields(
    fields=["investor_full_name", "commitment_amount"],
    context="LP Subscription Agreement",
)
```

## Use the no-op adapter (testing)

```python
from pdf_autofillr_plugins.builtin.llm_adapters.noop_llm_adapter import NoOpLLMAdapter

adapter = NoOpLLMAdapter(config={
    "mapping": {"investor_full_name": "investor_name"}  # optional override
})
adapter.initialize()
result = adapter.map_fields(["investor_full_name", "email"], "any context")
# {"investor_full_name": "investor_name", "email": "email"}  (override + passthrough)
```

## Expected output

```
{"investor_full_name": "investor_name", "commitment_amount_usd": "commitment_usd"}
```
