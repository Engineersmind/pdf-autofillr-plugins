"""
Basic usage — load and use the built-in email validator.

    pip install pdf-autofillr-plugins
    python examples/basic_usage.py
"""
from __future__ import annotations

from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin


def main() -> None:
    manager = PluginManager()
    manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
    validator = manager.load_plugin("email-validator", "validator")

    print(f"\n  Plugin: {validator.name}  v{validator.version}")
    print("  " + "─" * 40)

    test_cases = [
        ("user@example.com",    True,  "valid business email"),
        ("bad-email",           False, "missing @ and domain"),
        ("test@tempmail.com",   True,  "valid but disposable domain warning"),
        ("user@gmail.com",      True,  "valid personal email"),
        (12345,                 False, "non-string value"),
        ("a" * 250 + "@x.com", False, "too long (>254 chars)"),
    ]

    for value, expected_valid, description in test_cases:
        result = validator.validate("email", value)
        icon = "✅" if result["valid"] else "✗ "
        status = "pass" if result["valid"] == expected_valid else "UNEXPECTED"
        display = str(value)[:35]
        print(f"  {icon}  {display:<37} [{status}]  {description}")
        if result["errors"]:
            print(f"         errors:   {result['errors']}")
        if result["warnings"]:
            print(f"         warnings: {result['warnings']}")

    manager.shutdown()
    print()


if __name__ == "__main__":
    main()
