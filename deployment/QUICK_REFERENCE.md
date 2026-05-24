# Quick Reference — pdf-autofillr-plugins

## Install

```bash
pip install pdf-autofillr-plugins
pip install "pdf-autofillr-plugins[dev]"   # + dev tools
```

## First-time setup

```bash
pdf-autofillr-plugins setup    # copy .env and usage/ guides
pdf-autofillr-plugins status   # check installation
```

## Use a built-in plugin

```python
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

manager = PluginManager()
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
validator = manager.load_plugin("email-validator", "validator")
print(validator.validate("email", "user@example.com"))
# {"valid": True, "errors": [], "warnings": [], "validator": "email-validator"}
```

## Write and discover your own plugin

```python
from pdf_autofillr_plugins import plugin, PluginManager
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(category="validator", name="my-validator")
class MyValidator(ValidatorPlugin):
    def get_metadata(self): ...
    def supports_field_type(self, ft): return True
    def validate(self, name, value, rules=None, **kw):
        return {"valid": True, "errors": [], "warnings": [], "validator": "my-validator"}

manager = PluginManager()
manager.discover_plugins(["./my_plugins/"])
p = manager.load_plugin("my-validator", "validator")
```

## Test

```bash
cd plugins && pytest tests/ -v
```

## Build & publish

```bash
make build
git tag plugins-v0.2.0 && git push origin plugins-v0.2.0   # CI publishes automatically
```

## CLI commands

```bash
pdf-autofillr-plugins setup              # first-time setup
pdf-autofillr-plugins status             # check installed modules + env
pdf-autofillr-plugins list --path ./my_plugins/   # discover plugins
pdf-autofillr-plugins --version          # show version
```
