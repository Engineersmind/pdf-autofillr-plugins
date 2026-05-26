# Plugin Discovery

The `PluginRegistry` can discover `@plugin`-decorated classes from:

1. **File system directories** — scans all `.py` files in the directory
2. **Python module paths** — walks sub-packages using `pkgutil`

→ Full reference: [plugins/USAGE.md — Section 6](../../plugins/USAGE.md#6-pluginregistry)

## From a directory

```python
from pdf_autofillr_plugins import PluginManager

manager = PluginManager()
discovered = manager.discover_plugins(["./my_plugins/"])
print(discovered)
# {"validator": ["phone-validator"], "extractor": ["my-extractor"]}
```

## From a Python module

```python
manager.discover_plugins(["my_company.pdf_plugins"])
```

## With category filter

```python
manager.discover_plugins(
    ["./my_plugins/", "my_company.plugins"],
    categories=["validator", "extractor"],
)
```

## At init time

```python
manager = PluginManager(plugin_paths=["./my_plugins/"])
```

## Manual registration (no discovery needed)

```python
from my_plugins.phone_validator import PhoneValidatorPlugin

manager.registry.register_plugin(PhoneValidatorPlugin, "validator", "phone-validator")
```

## Discovery rules

- Files starting with `_` are skipped (e.g. `__init__.py`)
- Only classes with `_is_plugin = True` (set by `@plugin`) are registered
- Classes must be a subclass of `BasePlugin`
- If the same plugin name is registered twice, the later registration wins
