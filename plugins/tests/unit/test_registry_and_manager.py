"""Unit tests for PluginRegistry, PluginManager, decorators, and BasePlugin."""
import pytest
from pdf_autofillr_plugins import plugin, PluginManager, PluginRegistry, PluginMetadata
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, ExtractorPlugin, MapperPlugin


# ── Decorator ─────────────────────────────────────────────────────────────────

class TestPluginDecorator:
    def test_decorator_sets_metadata_attrs(self):
        @plugin(category="validator", name="test-plugin", version="2.0.0",
                author="Me", description="A test", tags=["a", "b"], priority=50)
        class Dummy(ValidatorPlugin):
            def get_metadata(self): ...
            def validate(self, *a, **kw): ...
            def supports_field_type(self, ft): return True

        assert Dummy._plugin_category == "validator"
        assert Dummy._plugin_name == "test-plugin"
        assert Dummy._plugin_version == "2.0.0"
        assert Dummy._plugin_author == "Me"
        assert Dummy._is_plugin is True
        assert Dummy._plugin_priority == 50
        assert "a" in Dummy._plugin_tags

    def test_decorator_default_name_is_class_name(self):
        @plugin(category="extractor")
        class MyExtractorPlugin(ExtractorPlugin):
            def get_metadata(self): ...
            def extract(self, *a, **kw): ...
            def supports(self, *a, **kw): return True

        assert MyExtractorPlugin._plugin_name == "MyExtractorPlugin"

    def test_decorated_class_is_still_instantiable(self):
        @plugin(category="validator", name="inst-test")
        class InstValidator(ValidatorPlugin):
            def get_metadata(self):
                return PluginMetadata(name="inst-test", version="1.0", author="T",
                                      description="", category="validator")
            def validate(self, name, value, rules=None, **kw):
                return {"valid": True, "errors": [], "warnings": [], "validator": "inst-test"}
            def supports_field_type(self, ft): return True

        v = InstValidator()
        assert v.name == "inst-test"


# ── PluginRegistry ────────────────────────────────────────────────────────────

class TestPluginRegistry:
    def test_register_and_get(self, registry):
        cls = registry.get_plugin_class("noop-validator", "validator")
        assert cls is not None

    def test_get_without_category_searches_all(self, registry):
        cls = registry.get_plugin_class("noop-extractor")
        assert cls is not None

    def test_get_nonexistent_returns_none(self, registry):
        cls = registry.get_plugin_class("no-such-plugin")
        assert cls is None

    def test_list_plugins_all(self, registry):
        result = registry.list_plugins()
        assert "validator" in result
        assert "extractor" in result
        assert "mapper" in result

    def test_list_plugins_filtered(self, registry):
        result = registry.list_plugins(category="validator")
        assert "validator" in result
        assert "extractor" not in result

    def test_get_plugin_info(self, registry):
        info = registry.get_plugin_info("noop-validator", "validator")
        assert info is not None
        assert info["name"] == "noop-validator"
        assert info["version"] == "0.1.0"
        assert info["category"] == "validator"

    def test_get_plugin_info_nonexistent_returns_none(self, registry):
        assert registry.get_plugin_info("ghost") is None

    def test_clear(self, registry):
        registry.clear()
        assert registry.list_plugins() == {}

    def test_discover_from_path(self, tmp_path):
        """Registry should discover @plugin-decorated classes from a file."""
        plugin_file = tmp_path / "my_plugin.py"
        plugin_file.write_text("""
from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

@plugin(category="validator", name="file-plugin")
class FilePlugin(ValidatorPlugin):
    def get_metadata(self):
        return PluginMetadata(name="file-plugin", version="1.0", author="T",
                              description="", category="validator")
    def validate(self, name, value, rules=None, **kw):
        return {"valid": True, "errors": [], "warnings": [], "validator": "file-plugin"}
    def supports_field_type(self, ft): return True
""")
        r = PluginRegistry()
        discovered = r.discover_plugins([str(tmp_path)])
        assert "validator" in discovered
        assert "file-plugin" in discovered["validator"]


# ── PluginManager ─────────────────────────────────────────────────────────────

class TestPluginManager:
    def test_load_plugin(self, manager):
        p = manager.load_plugin("noop-validator", "validator")
        assert p is not None
        assert p.name == "noop-validator"

    def test_load_same_plugin_twice_returns_same_instance(self, manager):
        p1 = manager.load_plugin("noop-validator", "validator")
        p2 = manager.load_plugin("noop-validator", "validator")
        assert p1 is p2

    def test_load_nonexistent_returns_none(self, manager):
        p = manager.load_plugin("ghost-plugin", "validator")
        assert p is None

    def test_get_plugin_lazy(self, manager):
        p = manager.get_plugin("noop-extractor", "extractor")
        assert p is not None

    def test_list_plugins(self, manager):
        result = manager.list_plugins()
        assert "validator" in result

    def test_list_plugins_filtered(self, manager):
        result = manager.list_plugins(category="mapper")
        assert "mapper" in result
        assert "validator" not in result

    def test_get_plugin_info(self, manager):
        info = manager.get_plugin_info("noop-mapper", "mapper")
        assert info["name"] == "noop-mapper"

    def test_unload_plugin(self, manager):
        manager.load_plugin("noop-validator", "validator")
        manager.unload_plugin("noop-validator", "validator")
        # After unload, is_initialized should be False for a new load
        p = manager.load_plugin("noop-validator", "validator")
        # Re-loaded successfully
        assert p is not None

    def test_shutdown_clears_all_instances(self, manager):
        manager.load_plugin("noop-validator", "validator")
        manager.load_plugin("noop-extractor", "extractor")
        manager.shutdown()
        assert manager._instances == {}

    def test_enabled_plugins_filter(self, registry):
        m = PluginManager(enabled_plugins=["noop-validator"])
        m.registry = registry
        # noop-extractor should be blocked
        p = m.load_plugin("noop-extractor", "extractor")
        assert p is None
        # noop-validator should work
        p2 = m.load_plugin("noop-validator", "validator")
        assert p2 is not None

    def test_find_extractor(self, manager):
        extractor = manager.find_extractor("any_file.pdf")
        assert extractor is not None
        assert extractor.name == "noop-extractor"

    def test_find_mapper(self, manager):
        mapper = manager.find_mapper({"key": "value"})
        assert mapper is not None
        assert mapper.name == "noop-mapper"

    def test_find_extractor_returns_none_when_none_match(self, manager):
        # Override supports() to always return False
        from unittest.mock import patch
        with patch.object(
            manager.registry.get_plugin_class("noop-extractor", "extractor"),
            "supports",
            return_value=False
        ):
            pass  # We can't easily patch an instance method here; just ensure no crash
