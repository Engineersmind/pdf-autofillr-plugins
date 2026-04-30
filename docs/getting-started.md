# Getting Started

## 1. Install

```bash
pip install pdf-autofillr-plugins
```

## 2. Write a plugin

```python
from pdf_autofillr_plugins import plugin, PluginManager
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(category="validator", name="my-validator")
class MyValidator(ValidatorPlugin):
    def get_metadata(self):
        return PluginMetadata(name="my-validator", version="1.0.0",
                              author="You", description="", category="validator")
    def validate(self, field_name, field_value, rules=None, **kwargs):
        return {"valid": True, "errors": [], "warnings": [], "validator": "my-validator"}
    def supports_field_type(self, ft): return True
```

## 3. Use it

```python
manager = PluginManager()
manager.registry.register_plugin(MyValidator, "validator", "my-validator")
v = manager.load_plugin("my-validator", "validator")
print(v.validate("email", "user@example.com"))
```

→ See [packages/plugins/quickstart.md](../packages/plugins/quickstart.md) for more.
→ See [packages/plugins/USAGE.md](../packages/plugins/USAGE.md) for full reference.
