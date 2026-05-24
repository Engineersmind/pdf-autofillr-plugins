# pdf-autofillr-plugins — Quick Start

Up and running in 2 minutes. No API keys. No runtime dependencies.

## Step 1 — Install

```bash
pip install pdf-autofillr-plugins
```

## Step 2 — First-time setup

```bash
pdf-autofillr-plugins setup    # creates .env and copies usage/ guides
pdf-autofillr-plugins status   # verify everything is ready
```

## Step 3 — Write your first plugin

Create `my_plugins/phone_validator.py`:

```python
import re
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(
    category="validator",
    name="phone-validator",
    version="1.0.0",
    author="Your Team",
    description="Validates E.164 phone numbers",
)
class PhoneValidatorPlugin(ValidatorPlugin):

    _E164 = re.compile(r"^\+[1-9]\d{6,14}$")

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="phone-validator", version="1.0.0",
            author="Your Team", description="E.164 phone validator",
            category="validator",
        )

    def supports_field_type(self, field_type: str) -> bool:
        return field_type.lower() in {"phone", "telephone", "mobile"}

    def validate(self, field_name, field_value, rules=None, **kwargs):
        errors = []
        if not self._E164.match(str(field_value)):
            errors.append(f"Expected E.164 format like +12125551234, got: {field_value!r}")
        return {
            "valid": not errors,
            "errors": errors,
            "warnings": [],
            "validator": "phone-validator",
            "field_name": field_name,
        }
```

## Step 4 — Use it

```python
from pdf_autofillr_plugins import PluginManager

manager = PluginManager()
manager.discover_plugins(["my_plugins/"])

validator = manager.load_plugin("phone-validator", "validator")
print(validator.validate("phone", "+12125551234"))
# {"valid": True, "errors": [], ...}

print(validator.validate("phone", "555-1234"))
# {"valid": False, "errors": ["Expected E.164 format..."], ...}

manager.shutdown()
```

## Built-in plugins (ready to use right now)

```python
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import InvoiceExtractorPlugin
from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin

manager = PluginManager()
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
manager.registry.register_plugin(IdentityMapperPlugin, "mapper",    "identity-mapper")
manager.registry.register_plugin(InvoiceExtractorPlugin,"extractor","invoice-extractor")
manager.registry.register_plugin(MLMapperPlugin,        "mapper",   "ml-mapper")

# Validate an email
validator = manager.load_plugin("email-validator", "validator")
print(validator.validate("email", "user@example.com"))

# Extract invoice fields
extractor = manager.find_extractor("my_invoice.pdf")  # auto-selects invoice-extractor
result = extractor.extract("my_invoice.pdf")
print(result["fields"])

# Map to schema
mapper = manager.load_plugin("identity-mapper", "mapper")
mapping = mapper.map_fields(result["fields"], {"invoice_number": "str"})
print(mapping["mapped_fields"])

manager.shutdown()
```

## Via the CLI

```bash
pdf-autofillr-plugins setup                          # first-time setup
pdf-autofillr-plugins status                         # check modules + env
pdf-autofillr-plugins list --path ./my_plugins/      # discover plugins
pdf-autofillr-plugins --version                      # show version
```

## Run the examples

```bash
python plugins/examples/custom_validator.py
python plugins/examples/custom_extractor.py
python plugins/examples/using_plugins.py
```

→ Full reference: [USAGE.md](USAGE.md)
