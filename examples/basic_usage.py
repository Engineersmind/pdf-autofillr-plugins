"""
Basic usage — load and use the built-in email validator.
"""
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

manager = PluginManager()
manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")

v = manager.load_plugin("email-validator", "validator")

for email in ["user@example.com", "bad-email", "test@tempmail.com"]:
    r = v.validate("email", email)
    icon = "✅" if r["valid"] else "✗ "
    print(f"{icon} {email}")
    if r["warnings"]: print(f"     warnings: {r['warnings']}")
    if r["errors"]:   print(f"     errors:   {r['errors']}")

manager.shutdown()
