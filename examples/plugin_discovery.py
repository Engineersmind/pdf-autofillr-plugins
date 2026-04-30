"""
Auto-discover plugins from a directory.
"""
import tempfile, os
from pdf_autofillr_plugins import PluginManager

# Write a plugin to a temp directory
plugin_code = '''
from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces.validator_plugin import ValidatorPlugin
from pdf_autofillr_plugins.interfaces.base_plugin import PluginMetadata

@plugin(category="validator", name="discovered-plugin", version="1.0.0")
class DiscoveredPlugin(ValidatorPlugin):
    def get_metadata(self):
        return PluginMetadata(name="discovered-plugin", version="1.0.0",
                              author="Auto", description="Auto-discovered", category="validator")
    def validate(self, name, value, rules=None, **kwargs):
        return {"valid": True, "errors": [], "warnings": [], "validator": "discovered-plugin"}
    def supports_field_type(self, ft): return True
'''

with tempfile.TemporaryDirectory() as tmpdir:
    with open(os.path.join(tmpdir, "my_plugin.py"), "w") as f:
        f.write(plugin_code)

    manager = PluginManager()
    discovered = manager.discover_plugins([tmpdir])
    print(f"Discovered: {discovered}")

    p = manager.load_plugin("discovered-plugin", "validator")
    print(f"Loaded: {p.name} v{p.version}")
    manager.shutdown()
