"""
pdf_autofillr_plugins.hooks
============================
Lifecycle hook definitions for the pdf-autofillr plugin pipeline.

Available hooks:
    pre_extract(pdf_bytes)  → pdf_bytes
    post_extract(schema)    → schema
    pre_fill(form_data)     → form_data
    post_fill(pdf_bytes)    → pdf_bytes
"""

from pdf_autofillr_plugins.hooks.base_hooks import (
    BaseHook,
    PreExtractHook,
    PostExtractHook,
    PreFillHook,
    PostFillHook,
    HookRegistry,
)

__all__ = [
    "BaseHook",
    "PreExtractHook",
    "PostExtractHook",
    "PreFillHook",
    "PostFillHook",
    "HookRegistry",
]