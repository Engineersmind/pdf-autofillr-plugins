"""
Example: using all built-in plugins together.

Shows the full discover → load → use → shutdown lifecycle.

    python examples/using_plugins.py
"""
from __future__ import annotations

from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import PassthroughExtractorPlugin
from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import InvoiceExtractorPlugin
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin


def main() -> None:
    print("\n=== Initializing Plugin Manager ===")
    manager = PluginManager(lazy_load=True)

    # Register all built-ins
    manager.registry.register_plugin(EmailValidatorPlugin,       "validator", "email-validator")
    manager.registry.register_plugin(PassthroughExtractorPlugin, "extractor", "passthrough-extractor")
    manager.registry.register_plugin(InvoiceExtractorPlugin,     "extractor", "invoice-extractor")
    manager.registry.register_plugin(IdentityMapperPlugin,       "mapper",    "identity-mapper")
    manager.registry.register_plugin(MLMapperPlugin,             "mapper",    "ml-mapper")

    # List everything
    print("\n=== Available Plugins ===")
    for category, names in manager.list_plugins().items():
        print(f"\n  {category.upper()}")
        for name in names:
            info = manager.get_plugin_info(name, category)
            print(f"    • {info['name']:<30} v{info['version']}  {info['description']}")

    # ── Email validator ───────────────────────────────────────────────────────
    print("\n=== Email Validator ===")
    validator = manager.load_plugin("email-validator", "validator")
    for email in ["user@example.com", "bad-email", "test@tempmail.com"]:
        r = validator.validate("email", email)
        icon = "✅" if r["valid"] else "✗ "
        print(f"  {icon} {email}")
        if r["errors"]:   print(f"       errors:   {r['errors']}")
        if r["warnings"]: print(f"       warnings: {r['warnings']}")

    # ── Invoice extractor ─────────────────────────────────────────────────────
    print("\n=== Invoice Extractor ===")
    extractor = manager.find_extractor("q1_invoice.pdf")
    if extractor:
        result = extractor.extract("q1_invoice.pdf")
        print(f"  Extractor: {extractor.name}")
        print(f"  Extracted {len(result['fields'])} fields:")
        for f in result["fields"]:
            print(f"    {f['name']:<20} = {f['value']}  ({f['confidence']:.0%})")
    else:
        print("  No extractor matched.")

    # ── Passthrough extractor ─────────────────────────────────────────────────
    print("\n=== Passthrough Extractor ===")
    raw_fields = [
        {"name": "investor_name",  "value": "Jane Smith",       "confidence": 0.99},
        {"name": "email_address",  "value": "jane@example.com", "confidence": 0.98},
        {"name": "commitment_usd", "value": "500000",           "confidence": 0.95},
    ]
    pt = PassthroughExtractorPlugin(config={"fields": raw_fields})
    pt.initialize()
    extraction = pt.extract("blank_form.pdf")
    print(f"  Extracted {len(extraction['fields'])} fields (passthrough)")

    # ── Identity mapper ───────────────────────────────────────────────────────
    print("\n=== Identity Mapper ===")
    schema = {"investor_name": "string", "email_address": "string", "commitment_usd": "string"}
    id_mapper = manager.load_plugin("identity-mapper", "mapper")
    mapping = id_mapper.map_fields(extraction["fields"], schema)
    print(f"  Coverage: {mapping['coverage']:.0%}")
    for k, v in mapping["mapped_fields"].items():
        print(f"    {k:<25} = {v}")

    # ── ML mapper ─────────────────────────────────────────────────────────────
    print("\n=== ML Mapper (synonym-based) ===")
    invoice_fields = [
        {"name": "first_name",     "value": "John",          "confidence": 0.9},
        {"name": "email",          "value": "john@corp.com", "confidence": 0.9},
        {"name": "invoice_number", "value": "INV-001",       "confidence": 0.9},
        {"name": "unknown_field",  "value": "???",           "confidence": 0.5},
    ]
    ml_mapper = manager.load_plugin("ml-mapper", "mapper")
    ml_result = ml_mapper.map_fields(invoice_fields)
    print(f"  Mapped:   {list(ml_result['mapped_fields'].keys())}")
    print(f"  Unmapped: {ml_result['unmapped_fields']}")

    # ── Shutdown ──────────────────────────────────────────────────────────────
    print("\n=== Shutdown ===")
    manager.shutdown()
    print("  All plugins shut down.\n")


if __name__ == "__main__":
    main()
