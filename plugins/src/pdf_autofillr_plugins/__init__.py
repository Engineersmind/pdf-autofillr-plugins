"""
pdf-autofillr-plugins

Plugin framework for extending pdf-autofillr modules.

Quick start:
    from pdf_autofillr_plugins import plugin, PluginManager
    from pdf_autofillr_plugins.interfaces import ValidatorPlugin, PluginMetadata

    @plugin(category="validator", name="my-validator")
    class MyValidator(ValidatorPlugin):
        ...

Built-in plugins (ready to use):
    from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin
    from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import PassthroughExtractorPlugin
    from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import InvoiceExtractorPlugin
    from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin
    from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin

Utilities:
    from pdf_autofillr_plugins.utils import Timer, safe_json_dumps, retry_with_backoff

Core interfaces:
    from pdf_autofillr_plugins.core import HandlerInterface, StorageInterface
"""

__version__ = "0.1.0"

from pdf_autofillr_plugins.decorators import plugin, requires
from pdf_autofillr_plugins.registry import PluginRegistry
from pdf_autofillr_plugins.manager import PluginManager
from pdf_autofillr_plugins.interfaces.base_plugin import BasePlugin, PluginMetadata

__all__ = [
    "plugin",
    "requires",
    "PluginRegistry",
    "PluginManager",
    "BasePlugin",
    "PluginMetadata",
]
