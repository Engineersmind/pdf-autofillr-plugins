# Getting Started — pdf-autofillr-plugins

## 1. Install

```bash
pip install pdf-autofillr-plugins
pip install "pdf-autofillr-plugins[dev]"   # adds pytest, black, mypy
```

Zero runtime dependencies. Pure Python 3.10+.

## 2. First-time setup

```bash
pdf-autofillr-plugins setup    # copies usage/ guides and creates .env
pdf-autofillr-plugins status   # verify installation
```

## 3. Write your first plugin

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
            errors.append(f"Expected E.164 format (+12125551234), got: {field_value!r}")
        return {
            "valid": not errors,
            "errors": errors,
            "warnings": [],
            "validator": "phone-validator",
            "field_name": field_name,
        }
```

## 4. Discover and use it

```python
from pdf_autofillr_plugins import PluginManager

manager = PluginManager()
manager.discover_plugins(["my_plugins/"])

validator = manager.load_plugin("phone-validator", "validator")
result = validator.validate("phone", "+12125551234")
print(result)
# {"valid": True, "errors": [], "warnings": [], "validator": "phone-validator"}

# Clean up
manager.shutdown()
```

## 5. Use a built-in plugin

```python
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

manager = PluginManager()
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")

validator = manager.load_plugin("email-validator", "validator")
print(validator.validate("email", "user@example.com"))
# {"valid": True, "errors": [], "warnings": []}
```

## 6. Run the example scripts

```bash
python plugins/examples/custom_validator.py    # phone validator demo
python plugins/examples/custom_extractor.py   # invoice extractor demo
python plugins/examples/using_plugins.py      # all built-ins together
```

→ Full API reference: [plugins/USAGE.md](../plugins/USAGE.md)
→ 2-minute quickstart: [plugins/quickstart.md](../plugins/quickstart.md)
