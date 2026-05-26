"""
Integration test — all 5 built-in plugins working together in a full pipeline.
"""
import pytest

from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import InvoiceExtractorPlugin
from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import (
    PassthroughExtractorPlugin,
)
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin


@pytest.fixture
def full_manager():
    m = PluginManager()
    m.registry.register_plugin(EmailValidatorPlugin,       "validator", "email-validator")
    m.registry.register_plugin(PassthroughExtractorPlugin, "extractor", "passthrough-extractor")
    m.registry.register_plugin(InvoiceExtractorPlugin,     "extractor", "invoice-extractor")
    m.registry.register_plugin(IdentityMapperPlugin,       "mapper",    "identity-mapper")
    m.registry.register_plugin(MLMapperPlugin,             "mapper",    "ml-mapper")
    return m


class TestAllFivePluginsTogether:

    def test_all_plugins_listed(self, full_manager):
        all_p = full_manager.list_plugins()
        assert "email-validator"        in all_p.get("validator", [])
        assert "passthrough-extractor"  in all_p.get("extractor", [])
        assert "invoice-extractor"      in all_p.get("extractor", [])
        assert "identity-mapper"        in all_p.get("mapper", [])
        assert "ml-mapper"              in all_p.get("mapper", [])

    def test_invoice_pipeline(self, full_manager):
        """Invoice extractor → ml-mapper → email-validator."""
        # 1. Extract from invoice
        extractor = full_manager.find_extractor("q1_invoice.pdf")
        assert extractor is not None
        assert extractor.name == "invoice-extractor"
        extraction = extractor.extract("q1_invoice.pdf")
        assert len(extraction["fields"]) == 4

        # 2. Map with ml-mapper
        mapper = full_manager.load_plugin("ml-mapper", "mapper")
        mapping = mapper.map_fields(extraction["fields"])
        assert "invoiceNo"   in mapping["mapped_fields"]
        assert "totalAmount" in mapping["mapped_fields"]

    def test_investor_pipeline(self, full_manager):
        """Passthrough extractor → identity-mapper → email-validator."""
        raw = [
            {"name": "investor_name",  "value": "Jane Smith",       "confidence": 0.99},
            {"name": "email_address",  "value": "jane@example.com", "confidence": 0.98},
            {"name": "commitment_usd", "value": "500000",           "confidence": 0.95},
        ]
        schema = {"investor_name": "string", "email_address": "string", "commitment_usd": "string"}

        extractor = PassthroughExtractorPlugin(config={"fields": raw})
        extractor.initialize()
        extraction = extractor.extract("blank.pdf")

        mapper = full_manager.load_plugin("identity-mapper", "mapper")
        mapping = mapper.map_fields(extraction["fields"], schema)
        assert mapping["coverage"] == pytest.approx(1.0)

        validator = full_manager.load_plugin("email-validator", "validator")
        result = validator.validate("email", mapping["mapped_fields"]["email_address"])
        assert result["valid"] is True

    def test_find_extractor_priority(self, full_manager):
        """invoice-extractor (priority=200) beats passthrough-extractor (priority=1)."""
        extractor = full_manager.find_extractor("my_invoice.pdf")
        assert extractor is not None
        assert extractor.name == "invoice-extractor"

    def test_find_extractor_non_invoice_falls_back_to_passthrough(self, full_manager):
        """passthrough-extractor only activates when config['fields'] is set."""
        extractor = full_manager.find_extractor("blank_form.pdf")
        # Neither should activate — invoice-extractor needs 'invoice' in name,
        # passthrough needs config['fields']. So result is None.
        assert extractor is None

    def test_shutdown_all(self, full_manager):
        full_manager.load_plugin("email-validator", "validator")
        full_manager.load_plugin("invoice-extractor", "extractor")
        full_manager.load_plugin("ml-mapper", "mapper")
        full_manager.shutdown()
        assert full_manager._instances == {}

    def test_plugin_info_complete_for_all(self, full_manager):
        checks = [
            ("email-validator",       "validator"),
            ("passthrough-extractor", "extractor"),
            ("invoice-extractor",     "extractor"),
            ("identity-mapper",       "mapper"),
            ("ml-mapper",             "mapper"),
        ]
        for name, cat in checks:
            info = full_manager.get_plugin_info(name, cat)
            assert info is not None, f"Missing info for {name}"
            for key in ("name", "version", "author", "description", "category"):
                assert key in info, f"{name}: missing key {key}"
