# ValidatorPlugin — Usage Guide

Validate any field value and return structured results.

## Minimum required files

```
my_plugins/
└── phone_validator.py
.env                         (optional — only if your validator calls an API)
```

## Minimum .env

```bash
# Only needed if your validator calls an external API
# MY_VALIDATOR_API_KEY=your_key_here
```

## Write the plugin

```python
# my_plugins/phone_validator.py
import re
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(category="validator", name="phone-validator", version="1.0.0", author="Your Team",
        description="Validates E.164 phone numbers")
class PhoneValidatorPlugin(ValidatorPlugin):

    _E164 = re.compile(r"^\+[1-9]\d{6,14}$")

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(name="phone-validator", version="1.0.0",
                              author="Your Team", description="E.164 phone validator",
                              category="validator")

    def supports_field_type(self, field_type: str) -> bool:
        return field_type.lower() in {"phone", "telephone", "mobile"}

    def validate(self, field_name, field_value, rules=None, **kwargs):
        errors = []
        if not self._E164.match(str(field_value)):
            errors.append(f"Expected E.164 format (+12125551234), got: {field_value!r}")
        return {"valid": not errors, "errors": errors, "warnings": [],
                "validator": "phone-validator", "field_name": field_name}
```

## Use it

```python
from pdf_autofillr_plugins import PluginManager

manager = PluginManager()
manager.discover_plugins(["my_plugins/"])

validator = manager.load_plugin("phone-validator", "validator")
result = validator.validate("phone", "+12125551234")
print(result)
# {"valid": True, "errors": [], "warnings": [], "validator": "phone-validator"}
```

## Expected output

```
{"valid": True, "errors": [], "warnings": [], "validator": "phone-validator", "field_name": "phone"}
```
