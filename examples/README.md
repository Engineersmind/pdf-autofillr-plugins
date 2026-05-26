# Examples — pdf-autofillr-plugins

Working examples for all major plugin patterns.

| File | Description |
|------|-------------|
| `basic_usage.py` | Load and use the built-in email validator |
| `full_pipeline.py` | Extract → map → validate using built-in plugins |
| `plugin_discovery.py` | Auto-discover plugins from a temp directory |
| `plugins/examples/custom_validator.py` | Write a phone number validator |
| `plugins/examples/custom_extractor.py` | Write an invoice PDF extractor |
| `plugins/examples/using_plugins.py` | All 5 built-in plugins working together |

## Run

```bash
pip install pdf-autofillr-plugins

# Top-level examples
python examples/basic_usage.py
python examples/full_pipeline.py
python examples/plugin_discovery.py

# Package-level examples
python plugins/examples/custom_validator.py
python plugins/examples/custom_extractor.py
python plugins/examples/using_plugins.py
```
