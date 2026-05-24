"""Shared fixtures for plugin tests."""
import pytest
from pdf_autofillr_plugins import PluginManager, PluginRegistry
from pdf_autofillr_plugins.interfaces.base_plugin import BasePlugin, PluginMetadata
from pdf_autofillr_plugins.decorators import plugin


# ── Minimal concrete implementations for testing ──────────────────────────────

@plugin(category="validator", name="noop-validator", version="0.1.0", author="Test")
class NoopValidator(
    __import__("pdf_autofillr_plugins.interfaces.validator_plugin", fromlist=["ValidatorPlugin"]).ValidatorPlugin
):
    def get_metadata(self):
        return PluginMetadata(name="noop-validator", version="0.1.0", author="Test",
                              description="No-op for tests", category="validator")
    def supports_field_type(self, ft): return True
    def validate(self, name, value, rules=None, **kw):
        return {"valid": True, "errors": [], "warnings": [], "validator": "noop-validator"}


@plugin(category="extractor", name="noop-extractor", version="0.1.0", author="Test")
class NoopExtractor(
    __import__("pdf_autofillr_plugins.interfaces.extractor_plugin", fromlist=["ExtractorPlugin"]).ExtractorPlugin
):
    def get_metadata(self):
        return PluginMetadata(name="noop-extractor", version="0.1.0", author="Test",
                              description="No-op for tests", category="extractor")
    def supports(self, pdf_path, **kw): return True
    def extract(self, pdf_path, strategy=None, **kw):
        return {"fields": [], "metadata": {}, "extractor": "noop-extractor"}


@plugin(category="mapper", name="noop-mapper", version="0.1.0", author="Test")
class NoopMapper(
    __import__("pdf_autofillr_plugins.interfaces.mapper_plugin", fromlist=["MapperPlugin"]).MapperPlugin
):
    def get_metadata(self):
        return PluginMetadata(name="noop-mapper", version="0.1.0", author="Test",
                              description="No-op for tests", category="mapper")
    def supports_schema(self, schema): return True
    def map_fields(self, fields, target_schema=None, **kw):
        return {"mapped_fields": {}, "mapping_info": [], "mapper": "noop-mapper"}


@pytest.fixture
def registry():
    r = PluginRegistry()
    r.register_plugin(NoopValidator, "validator", "noop-validator")
    r.register_plugin(NoopExtractor, "extractor", "noop-extractor")
    r.register_plugin(NoopMapper, "mapper", "noop-mapper")
    return r


@pytest.fixture
def manager(registry):
    m = PluginManager()
    m.registry = registry
    return m
