"""
Base Hook Definitions

Lifecycle hooks for the pdf-autofillr pipeline.

Hook execution order:
    1. pre_extract(pdf_bytes)   → pdf_bytes   — before PDF field extraction
    2. post_extract(schema)     → schema      — after extraction, before mapping
    3. pre_fill(form_data)      → form_data   — before PDF is filled
    4. post_fill(pdf_bytes)     → pdf_bytes   — after PDF is filled

Usage::

    from pdf_autofillr_plugins.hooks import PreExtractHook, HookRegistry
    from pdf_autofillr_plugins import plugin

    @plugin(category="hook", name="my-pre-extract-hook")
    class MyPreExtractHook(PreExtractHook):

        def pre_extract(self, pdf_bytes: bytes) -> bytes:
            # e.g. decrypt, watermark-strip, resize
            return pdf_bytes

    # Register and run
    registry = HookRegistry()
    registry.register(MyPreExtractHook())
    pdf_bytes = registry.run_pre_extract(pdf_bytes)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseHook(ABC):
    """
    Base class for all lifecycle hooks.

    All hooks have a name, priority, and enabled flag.
    Higher priority hooks run first.
    """

    #: Override in subclass or set via @plugin decorator
    name: str = "base-hook"
    priority: int = 100
    enabled: bool = True

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', priority={self.priority})"


class PreExtractHook(BaseHook):
    """
    Hook called before PDF field extraction.

    Receives raw PDF bytes, returns (optionally modified) PDF bytes.
    Use for: decryption, sanitisation, format normalisation.
    """

    @abstractmethod
    def pre_extract(self, pdf_bytes: bytes) -> bytes:
        """
        Process PDF bytes before extraction.

        Args:
            pdf_bytes: Raw bytes of the input PDF.

        Returns:
            PDF bytes to pass to the extractor (may be modified).
        """
        pass


class PostExtractHook(BaseHook):
    """
    Hook called after PDF field extraction, before mapping.

    Receives the extracted schema dict, returns (optionally modified) schema.
    Use for: field filtering, confidence thresholding, schema augmentation.
    """

    @abstractmethod
    def post_extract(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process extracted schema after extraction.

        Args:
            schema: Extracted field schema from the extractor plugin.

        Returns:
            Schema dict to pass to the mapper (may be modified).
        """
        pass


class PreFillHook(BaseHook):
    """
    Hook called before the PDF is filled with data.

    Receives the form data dict, returns (optionally modified) form data.
    Use for: data enrichment, value transformation, validation pre-check.
    """

    @abstractmethod
    def pre_fill(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process form data before PDF filling.

        Args:
            form_data: Mapped field data ready to be written into the PDF.

        Returns:
            Form data dict to pass to the filler (may be modified).
        """
        pass


class PostFillHook(BaseHook):
    """
    Hook called after the PDF has been filled.

    Receives filled PDF bytes, returns (optionally modified) PDF bytes.
    Use for: digital signing, watermarking, compression, audit logging.
    """

    @abstractmethod
    def post_fill(self, pdf_bytes: bytes) -> bytes:
        """
        Process filled PDF bytes after filling.

        Args:
            pdf_bytes: Raw bytes of the filled output PDF.

        Returns:
            PDF bytes to return to the caller (may be modified).
        """
        pass


class HookRegistry:
    """
    Registry for managing and executing lifecycle hooks.

    Hooks of the same type are sorted by priority (higher runs first)
    and executed in sequence — each hook's output feeds the next.

    Usage::

        registry = HookRegistry()
        registry.register(MyPreExtractHook())
        registry.register(MyPostFillHook())

        pdf_bytes = registry.run_pre_extract(raw_pdf_bytes)
        pdf_bytes = registry.run_post_fill(filled_pdf_bytes)
    """

    def __init__(self) -> None:
        self._pre_extract: List[PreExtractHook] = []
        self._post_extract: List[PostExtractHook] = []
        self._pre_fill: List[PreFillHook] = []
        self._post_fill: List[PostFillHook] = []

    def register(self, hook: BaseHook) -> None:
        """
        Register a hook instance into the appropriate list.

        Args:
            hook: Any hook instance (PreExtractHook, PostFillHook, etc.)

        Raises:
            TypeError: If hook is not a recognised BaseHook subclass.
        """
        if isinstance(hook, PreExtractHook):
            self._pre_extract.append(hook)
            self._pre_extract.sort(key=lambda h: h.priority, reverse=True)
        elif isinstance(hook, PostExtractHook):
            self._post_extract.append(hook)
            self._post_extract.sort(key=lambda h: h.priority, reverse=True)
        elif isinstance(hook, PreFillHook):
            self._pre_fill.append(hook)
            self._pre_fill.sort(key=lambda h: h.priority, reverse=True)
        elif isinstance(hook, PostFillHook):
            self._post_fill.append(hook)
            self._post_fill.sort(key=lambda h: h.priority, reverse=True)
        else:
            raise TypeError(f"Unknown hook type: {type(hook)}")

    def unregister(self, hook: BaseHook) -> None:
        """Remove a hook instance from the registry."""
        for lst in (self._pre_extract, self._post_extract, self._pre_fill, self._post_fill):
            if hook in lst:
                lst.remove(hook)
                return

    def run_pre_extract(self, pdf_bytes: bytes) -> bytes:
        """
        Run all registered PreExtractHooks in priority order.

        Args:
            pdf_bytes: Input PDF bytes.

        Returns:
            PDF bytes after all hooks have processed them.
        """
        for hook in self._pre_extract:
            if hook.enabled:
                try:
                    pdf_bytes = hook.pre_extract(pdf_bytes)
                except Exception as e:
                    print(f"PreExtractHook '{hook.name}' error: {e}")
        return pdf_bytes

    def run_post_extract(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all registered PostExtractHooks in priority order.

        Args:
            schema: Extracted field schema.

        Returns:
            Schema after all hooks have processed it.
        """
        for hook in self._post_extract:
            if hook.enabled:
                try:
                    schema = hook.post_extract(schema)
                except Exception as e:
                    print(f"PostExtractHook '{hook.name}' error: {e}")
        return schema

    def run_pre_fill(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all registered PreFillHooks in priority order.

        Args:
            form_data: Mapped form data.

        Returns:
            Form data after all hooks have processed it.
        """
        for hook in self._pre_fill:
            if hook.enabled:
                try:
                    form_data = hook.pre_fill(form_data)
                except Exception as e:
                    print(f"PreFillHook '{hook.name}' error: {e}")
        return form_data

    def run_post_fill(self, pdf_bytes: bytes) -> bytes:
        """
        Run all registered PostFillHooks in priority order.

        Args:
            pdf_bytes: Filled PDF bytes.

        Returns:
            PDF bytes after all hooks have processed them.
        """
        for hook in self._post_fill:
            if hook.enabled:
                try:
                    pdf_bytes = hook.post_fill(pdf_bytes)
                except Exception as e:
                    print(f"PostFillHook '{hook.name}' error: {e}")
        return pdf_bytes

    def list_hooks(self) -> Dict[str, List[str]]:
        """Return a summary of all registered hooks by type."""
        return {
            "pre_extract": [h.name for h in self._pre_extract],
            "post_extract": [h.name for h in self._post_extract],
            "pre_fill": [h.name for h in self._pre_fill],
            "post_fill": [h.name for h in self._post_fill],
        }

    def clear(self) -> None:
        """Unregister all hooks."""
        self._pre_extract.clear()
        self._post_extract.clear()
        self._pre_fill.clear()
        self._post_fill.clear()
