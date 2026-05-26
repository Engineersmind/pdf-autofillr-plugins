"""
pdf_autofillr_plugins.core

Shared cross-module abstractions originally from plugins/core in sdk-exp.

Provides:
  - HandlerInterface / BaseHandler / HandlerRequest / HandlerResponse
  - StorageInterface / StorageConfig / StorageProvider / create_storage
"""

from pdf_autofillr_plugins.core.handler_interface import (
    BaseHandler,
    HandlerInterface,
    HandlerRequest,
    HandlerResponse,
    OperationStatus,
)
from pdf_autofillr_plugins.core.storage_interface import (
    StorageConfig,
    StorageInterface,
    StorageProvider,
    create_storage,
)

__all__ = [
    "BaseHandler",
    "HandlerInterface",
    "HandlerRequest",
    "HandlerResponse",
    "OperationStatus",
    "StorageConfig",
    "StorageInterface",
    "StorageProvider",
    "create_storage",
]
