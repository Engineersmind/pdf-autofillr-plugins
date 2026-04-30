# Quick Reference — pdf-autofillr-plugins

```bash
# Install
pip install pdf-autofillr-plugins

# Use a built-in plugin
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
from pdf_autofillr_plugins import PluginManager

manager = PluginManager()
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
v = manager.load_plugin("email-validator", "validator")
print(v.validate("email", "user@example.com"))

# Discover from a directory
manager.discover_plugins(["./my_plugins/"])

# Test
cd packages/plugins && pytest tests/ -v

# Build & publish
make build && make publish
```
