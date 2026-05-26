"""
Auto-discover plugins from a directory.

    pip install pdf-autofillr-plugins
    python examples/plugin_discovery.py
"""

from __future__ import annotations

import os
import tempfile

from pdf_autofillr_plugins import PluginManager

PLUGIN_CODE = """
from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces.validator_plugin import ValidatorPlugin
from pdf_autofillr_plugins.interfaces.base_plugin import PluginMetadata

@plugin(category="validator", name="discovered-plugin", version="1.0.0",
        author="Auto", description="Auto-discovered example plugin")
class DiscoveredPlugin(ValidatorPlugin):
    def get_metadata(self):
        return PluginMetadata(name="discovered-plugin", version="1.0.0",
                              author="Auto", description="Auto-discovered example plugin",
                              category="validator")
    def validate(self, name, value, rules=None, **kwargs):
        return {"valid": True, "errors": [], "warnings": [], "validator": "discovered-plugin",
                "field_name": name, "field_value": value}
    def supports_field_type(self, ft): return True
"""


def main() -> None:
    print("\n  ── Plugin Discovery Example ──────────────────────────")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write a plugin to a temp directory
        plugin_file = os.path.join(tmpdir, "my_plugin.py")
        with open(plugin_file, "w") as f:
            f.write(PLUGIN_CODE)

        print(f"\n  Plugin file written to: {plugin_file}")

        # Discover it
        manager = PluginManager()
        discovered = manager.discover_plugins([tmpdir])
        print(f"  Discovered: {discovered}")

        # Load and use it
        plugin = manager.load_plugin("discovered-plugin", "validator")
        if plugin:
            print(f"  Loaded:  {plugin.name}  v{plugin.version}  ({plugin.category})")
            print(f"  Tags:    {plugin.tags}")
            result = plugin.validate("test_field", "test_value")  # type: ignore[union-attr, attr-defined]
            print(f"  Result:  {result}")

        # List all registered plugins
        all_plugins = manager.list_plugins()
        print(f"  All registered: {all_plugins}")

        manager.shutdown()
        print("  Shutdown complete.\n")


if __name__ == "__main__":
    main()
