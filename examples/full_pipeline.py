"""
Full extract → map → validate pipeline using built-in plugins.

    pip install pdf-autofillr-plugins
    python examples/full_pipeline.py
"""

from __future__ import annotations

from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import (
    InvoiceExtractorPlugin,
)
from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import (
    PassthroughExtractorPlugin,
)
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin
from pdf_autofillr_plugins.builtin.validators.email_validator import (
    EmailValidatorPlugin,
)


def investor_pipeline() -> None:
    """Simulates an investor onboarding form: extract → map → validate."""
    print("\n  ── Investor Onboarding Pipeline ──────────────────────")

    raw_fields = [
        {"name": "investor_name", "value": "Jane Smith", "confidence": 0.99},
        {"name": "email_address", "value": "jane@example.com", "confidence": 0.98},
        {"name": "commitment_usd", "value": "500000", "confidence": 0.95},
        {"name": "unknown_field", "value": "???", "confidence": 0.5},
    ]
    schema = {
        "investor_name": "string",
        "email_address": "string",
        "commitment_usd": "string",
    }

    manager = PluginManager()
    manager.registry.register_plugin(
        PassthroughExtractorPlugin, "extractor", "passthrough-extractor"
    )
    manager.registry.register_plugin(IdentityMapperPlugin, "mapper", "identity-mapper")
    manager.registry.register_plugin(
        EmailValidatorPlugin, "validator", "email-validator"
    )

    # 1. Extract
    extractor = PassthroughExtractorPlugin(config={"fields": raw_fields})
    extractor.initialize()
    extraction = extractor.extract("blank_lp_form.pdf")
    print(f"\n  1. Extracted {len(extraction['fields'])} fields")

    # 2. Map
    mapper = manager.load_plugin("identity-mapper", "mapper")
    assert mapper is not None
    mapping = mapper.map_fields(extraction["fields"], schema)  # type: ignore[union-attr, attr-defined]
    print(
        f"  2. Mapped {len(mapping['mapped_fields'])}/{len(extraction['fields'])} fields  "
        f"(coverage: {mapping['coverage']:.0%})"
    )
    for field, value in mapping["mapped_fields"].items():
        print(f"       {field:<20} = {value}")
    if mapping["unmapped_fields"]:
        print(f"     Unmapped: {mapping['unmapped_fields']}")

    # 3. Validate email
    validator = manager.load_plugin("email-validator", "validator")
    assert validator is not None
    email_value = mapping["mapped_fields"].get("email_address", "")
    result = validator.validate("email_address", email_value)  # type: ignore[union-attr, attr-defined]
    icon = "✅" if result["valid"] else "✗ "
    print(f"  3. Email validation: {icon} {email_value}")

    manager.shutdown()


def invoice_pipeline() -> None:
    """Simulates an invoice processing pipeline: extract → ml-map."""
    print("\n  ── Invoice Processing Pipeline ───────────────────────")

    manager = PluginManager()
    manager.registry.register_plugin(
        InvoiceExtractorPlugin, "extractor", "invoice-extractor"
    )
    manager.registry.register_plugin(MLMapperPlugin, "mapper", "ml-mapper")

    # 1. Find best extractor automatically
    extractor = manager.find_extractor("q1_invoice.pdf")
    if extractor:
        extraction = extractor.extract("q1_invoice.pdf")
        print(
            f"\n  1. Extractor: {extractor.name}  ({len(extraction['fields'])} fields)"
        )
        for f in extraction["fields"]:
            print(f"       {f['name']:<20} = {f['value']}  ({f['confidence']:.0%})")

        # 2. ML mapper (synonym table)
        mapper = manager.find_mapper({})
        if mapper:
            mapping = mapper.map_fields(extraction["fields"])
            print(f"  2. Mapper: {mapper.name}  (coverage: {mapping['coverage']:.0%})")
            for src, tgt in [
                (i["source"], i["target"]) for i in mapping["mapping_info"]
            ]:
                print(f"       {src:<20} → {tgt}")

    manager.shutdown()


if __name__ == "__main__":
    investor_pipeline()
    invoice_pipeline()
    print()
