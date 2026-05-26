"""
pdf_autofillr_plugins.registry
================================
Community-submitted plugin manifests live in this folder as JSON files.

Each .json file is a plugin manifest validated against plugin.schema.json.
The PluginLoader reads these manifests at runtime and registers the plugins
into the PluginRegistry.

Manifest format (plugin.schema.json):
    {
        "name":        "my-plugin",
        "version":     "1.0.0",
        "author":      "Your Name",
        "description": "What this plugin does",
        "category":    "extractor",
        "module":      "my_package.my_plugin",
        "class":       "MyPlugin",
        "tags":        ["custom", "extractor"],
        "requires":    ["some-package>=1.0"]
    }

To submit a community plugin:
    1. Implement your plugin using the pdf_autofillr_plugins interfaces
    2. Create a manifest JSON following the schema above
    3. Open a PR adding your manifest to this folder
"""

from pdf_autofillr_plugins.registry.plugin_registry import PluginRegistry

__all__ = ["PluginRegistry"]