"""
pdf_autofillr_plugins.loader
=============================
Runtime plugin loader — loads community plugin manifests from the
registry/ folder and feeds them into the PluginRegistry.
"""

from pdf_autofillr_plugins.loader.plugin_loader import PluginLoader

__all__ = ["PluginLoader"]
