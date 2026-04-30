"""
Example: writing a custom ValidatorPlugin.

    pip install pdf-autofillr-plugins
    python examples/custom_validator.py
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from pdf_autofillr_plugins import plugin, PluginManager
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata


@plugin(
    category="validator",
    name="phone-validator",
    version="1.0.0",
    author="Your Team",
    description="Validates E.164 international phone numbers",
    tags=["phone", "validation"],
)
class PhoneValidatorPlugin(ValidatorPlugin):
    """
    Validates phone numbers in E.164 format (+12125551234).
    """

    _E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="phone-validator",
            version="1.0.0",
            author="Your Team",
            description="Validates E.164 international phone numbers",
            category="validator",
            tags=["phone", "validation"],
        )

    def supports_field_type(self, field_type: str) -> bool:
        return field_type.lower() in {"phone", "phone_number", "telephone", "mobile"}

    def validate(
        self,
        field_name: str,
        field_value: Any,
        rules: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        errors = []
        warnings = []

        if not isinstance(field_value, str):
            errors.append("Phone number must be a string")
        elif not self._E164_RE.match(field_value):
            errors.append(
                f"Invalid phone number: {field_value!r}. Expected E.164 format (+12125551234)"
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validator": "phone-validator",
            "field_name": field_name,
            "field_value": field_value,
        }


if __name__ == "__main__":
    manager = PluginManager()
    manager.registry.register_plugin(PhoneValidatorPlugin, "validator", "phone-validator")

    validator = manager.load_plugin("phone-validator", "validator")
    assert validator is not None, "Plugin failed to load"

    tests = [
        ("+12125551234", True),
        ("555-1234",     False),
        ("+1",           False),
        ("+447911123456", True),
    ]
    print("\nPhone Validator Results")
    print("─" * 40)
    for number, expected_valid in tests:
        result = validator.validate("phone", number)
        icon = "✅" if result["valid"] else "✗"
        status = "pass" if result["valid"] == expected_valid else "FAIL"
        print(f"  {icon}  {number:<20}  [{status}]")
        if result["errors"]:
            print(f"       {result['errors'][0]}")
    print()
