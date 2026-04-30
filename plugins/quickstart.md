# pdf-autofillr-plugins — Quick Start

Up and running in 2 minutes. No API keys, no runtime dependencies.

## Step 1 — Install

```bash
pip install pdf-autofillr-plugins
```

## Step 2 — Write your first plugin

Create `my_plugins/phone_validator.py`:

```python
import re
from typing import Any, Dict, Optional
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
            author="Your Team", description="Validates E.164 phone numbers",
            category="validator",
        )

    def supports_field_type(self, field_type: str) -> bool:
        return field_type.lower() in {"phone", "telephone", "mobile"}

    def validate(self, field_name, field_value, rules=None, **kwargs):
        errors = []
        if not self._E164.match(str(field_value)):
            errors.append(f"Expected E.164 format like +12125551234, got: {field_value!r}")
        return {"valid": not errors, "errors": errors, "warnings": [], "validator": "phone-validator"}
```

## Step 3 — Use it

```python
from pdf_autofillr_plugins import PluginManager

# Auto-discover from your plugins directory
manager = PluginManager()
manager.discover_plugins(["my_plugins/"])

# Load and use
validator = manager.load_plugin("phone-validator", "validator")
result = validator.validate("phone", "+12125551234")
print(result)  # {"valid": True, "errors": [], ...}
```

## Built-in plugins (ready to use)

```python
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin

manager = PluginManager()
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
manager.registry.register_plugin(IdentityMapperPlugin, "mapper", "identity-mapper")

# Validate an email
validator = manager.load_plugin("email-validator", "validator")
print(validator.validate("email", "user@example.com"))

# Map fields to a schema
mapper = manager.load_plugin("identity-mapper", "mapper")
print(mapper.map_fields(
    [{"name": "investor_name", "value": "Jane", "confidence": 1.0}],
    target_schema={"investor_name": "string"},
))
```

→ Full reference: [USAGE.md](USAGE.md)
