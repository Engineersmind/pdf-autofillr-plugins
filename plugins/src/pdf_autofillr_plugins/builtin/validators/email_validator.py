"""
Built-in: EmailValidatorPlugin

Validates email address fields.
Registered automatically under category="validator", name="email-validator".
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import PluginMetadata, ValidatorPlugin


@plugin(
    category="validator",
    name="email-validator",
    version="1.0.0",
    author="PDF AutoFillr Team",
    description="Validates email address fields — format, length, and disposable domain checks",
    tags=["email", "validation", "builtin"],
)
class EmailValidatorPlugin(ValidatorPlugin):
    """
    Built-in email validator.

    Rules applied (in order):
    1. Value must be a string.
    2. Must match RFC-5321 format.
    3. Must be ≤ 254 characters.
    4. Warns on known disposable domains.
    5. Honours optional caller-supplied rules:
       - require_corporate: warns on gmail/yahoo/hotmail
       - allowed_domains: list[str] — error if domain not in list
    """

    _EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

    _DISPOSABLE = {
        "tempmail.com",
        "throwaway.email",
        "guerrillamail.com",
        "mailinator.com",
        "yopmail.com",
        "sharklasers.com",
    }

    _PERSONAL = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"}

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="email-validator",
            version="1.0.0",
            author="PDF AutoFillr Team",
            description="Validates email address fields",
            category="validator",
            tags=["email", "validation", "builtin"],
        )

    def supports_field_type(self, field_type: str) -> bool:
        return field_type.lower() in {
            "email",
            "email_address",
            "emailaddress",
            "e-mail",
        }

    def validate(
        self,
        field_name: str,
        field_value: Any,
        rules: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        rules = rules or {}
        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(field_value, str):
            return {
                "valid": False,
                "errors": ["Email must be a string"],
                "warnings": [],
                "validator": "email-validator",
                "field_name": field_name,
            }

        if not self._EMAIL_RE.match(field_value):
            errors.append(f"Invalid email format: {field_value!r}")

        if len(field_value) > 254:
            errors.append("Email address exceeds 254 characters (RFC 5321)")

        domain = field_value.split("@")[-1].lower() if "@" in field_value else ""

        if domain in self._DISPOSABLE:
            warnings.append(f"Disposable email domain detected: {domain}")

        if rules.get("require_corporate") and domain in self._PERSONAL:
            warnings.append(f"Personal email domain detected: {domain}")

        allowed = rules.get("allowed_domains")
        if allowed and domain not in allowed:
            errors.append(f"Email domain not in allowed list: {domain}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validator": "email-validator",
            "field_name": field_name,
            "field_value": field_value,
        }

    def get_validation_rules(self) -> Dict[str, Any]:
        return {
            "require_corporate": False,
            "allowed_domains": None,
        }
