"""
Integration tests — full plugin lifecycle end-to-end.
No external dependencies required.
"""
import pytest
# from pdf_autofillr_plugins import PluginManager, PluginRegistry, plugin
from pdf_autofillr_plugins import PluginManager
# from pdf_autofillr_plugins.interfaces import (
#     ValidatorPlugin, ExtractorPlugin, MapperPlugin, PluginMetadata,
# )
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import PassthroughExtractorPlugin
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin


class TestFullPipelineIntegration:
    """
    Simulate a complete extraction → mapping → validation pipeline
    using only built-in plugins.
    """

    def _make_manager(self) -> PluginManager:
        m = PluginManager()
        m.registry.register_plugin(EmailValidatorPlugin,       "validator", "email-validator")
        m.registry.register_plugin(PassthroughExtractorPlugin, "extractor", "passthrough-extractor")
        m.registry.register_plugin(IdentityMapperPlugin,       "mapper",    "identity-mapper")
        return m

    def test_extract_then_map_then_validate(self):
        raw_fields = [
            {"name": "investor_name",  "value": "Jane Smith",        "confidence": 0.99},
            {"name": "email_address",  "value": "jane@example.com",  "confidence": 0.98},
            {"name": "commitment_usd", "value": "500000",             "confidence": 0.95},
        ]
        schema = {
            "investor_name":  "string",
            "email_address":  "string",
            "commitment_usd": "string",
        }

        manager = self._make_manager()

        # Step 1: extract
        extractor = PassthroughExtractorPlugin(config={"fields": raw_fields})
        extractor.initialize()
        extraction = extractor.extract("blank_form.pdf")
        assert len(extraction["fields"]) == 3

        # Step 2: map
        mapper = manager.load_plugin("identity-mapper", "mapper")
        mapping = mapper.map_fields(extraction["fields"], schema)
        assert mapping["coverage"] == pytest.approx(1.0)
        assert mapping["mapped_fields"]["email_address"] == "jane@example.com"

        # Step 3: validate email
        validator = manager.load_plugin("email-validator", "validator")
        result = validator.validate("email_address", mapping["mapped_fields"]["email_address"])
        assert result["valid"] is True

    def test_invalid_email_caught_after_mapping(self):
        raw_fields = [{"name": "email_address", "value": "not-an-email", "confidence": 0.5}]
        schema = {"email_address": "string"}

        manager = self._make_manager()

        extractor = PassthroughExtractorPlugin(config={"fields": raw_fields})
        extractor.initialize()
        extraction = extractor.extract("form.pdf")

        mapper = manager.load_plugin("identity-mapper", "mapper")
        mapping = mapper.map_fields(extraction["fields"], schema)

        validator = manager.load_plugin("email-validator", "validator")
        result = validator.validate("email_address", mapping["mapped_fields"]["email_address"])
        assert result["valid"] is False

    def test_plugin_lifecycle_init_and_shutdown(self):
        manager = self._make_manager()

        p = manager.load_plugin("email-validator", "validator")
        assert p.is_initialized is True

        manager.unload_plugin("email-validator", "validator")
        assert "validator:email-validator" not in manager._instances

        manager.shutdown()
        assert manager._instances == {}

    def test_list_all_registered_plugins(self):
        manager = self._make_manager()
        all_plugins = manager.list_plugins()

        assert "validator" in all_plugins
        assert "extractor" in all_plugins
        assert "mapper" in all_plugins
        assert "email-validator" in all_plugins["validator"]
        assert "passthrough-extractor" in all_plugins["extractor"]
        assert "identity-mapper" in all_plugins["mapper"]

    def test_plugin_info_complete(self):
        manager = self._make_manager()
        info = manager.get_plugin_info("email-validator", "validator")
        for key in ["name", "version", "author", "description", "category", "tags"]:
            assert key in info, f"Missing key: {key}"

    def test_discover_plugins_from_directory(self, tmp_path):
        """Discover a freshly written plugin file from a temp directory."""
        (tmp_path / "my_plugin.py").write_text("""
from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces.validator_plugin import ValidatorPlugin
from pdf_autofillr_plugins.interfaces.base_plugin import PluginMetadata

@plugin(category="validator", name="discovered-plugin", version="9.9.9")
class DiscoveredPlugin(ValidatorPlugin):
    def get_metadata(self):
        return PluginMetadata(name="discovered-plugin", version="9.9.9",
                              author="T", description="", category="validator")
    def validate(self, name, value, rules=None, **kw):
        return {"valid": True, "errors": [], "warnings": [], "validator": "discovered-plugin"}
    def supports_field_type(self, ft): return True
""")
        manager = PluginManager()
        discovered = manager.discover_plugins([str(tmp_path)])
        assert "validator" in discovered
        assert "discovered-plugin" in discovered["validator"]

        p = manager.load_plugin("discovered-plugin", "validator")
        assert p is not None
        assert p.version == "9.9.9"
