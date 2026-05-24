# Built-in Plugins

Five plugins ship ready to use. No configuration needed unless noted.

→ Full reference: [plugins/USAGE.md — Section 8](../../plugins/USAGE.md#8-built-in-plugins)

## Summary

| Plugin | Import | Category | Priority |
|--------|--------|----------|----------|
| `EmailValidatorPlugin` | `pdf_autofillr_plugins.builtin.validators.email_validator` | validator | 100 |
| `PassthroughExtractorPlugin` | `pdf_autofillr_plugins.builtin.extractors.passthrough_extractor` | extractor | 1 |
| `InvoiceExtractorPlugin` | `pdf_autofillr_plugins.builtin.extractors.invoice_extractor` | extractor | 200 |
| `IdentityMapperPlugin` | `pdf_autofillr_plugins.builtin.mappers.identity_mapper` | mapper | 1 |
| `MLMapperPlugin` | `pdf_autofillr_plugins.builtin.mappers.ml_mapper` | mapper | 150 |

## Quick usage

```python
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin

manager = PluginManager()
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
manager.registry.register_plugin(IdentityMapperPlugin, "mapper", "identity-mapper")

validator = manager.load_plugin("email-validator", "validator")
mapper    = manager.load_plugin("identity-mapper", "mapper")

# Validate
print(validator.validate("email", "user@company.com"))

# Map
fields = [{"name": "investor_name", "value": "Jane", "confidence": 1.0}]
print(mapper.map_fields(fields, {"investor_name": "string"}))
```
