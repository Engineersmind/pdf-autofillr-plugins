"""
Unit tests for:
- pdf_autofillr_plugins.utils (Timer, retry, hashing, JSON, string helpers)
- pdf_autofillr_plugins.decorators (@requires, @cache_result, @pre_execute, @post_execute)
- ChunkerPlugin, EmbedderPlugin, FillerPlugin, TransformerPlugin interfaces
- ValidatorPlugin.validate_batch()
- ExtractorPlugin.get_supported_strategies(), validate_pdf()
- MapperPlugin.get_mapping_confidence(), validate_mapping()
- BasePlugin.tags, priority, repr, str
"""

from __future__ import annotations

import json
import time

import pytest

from pdf_autofillr_plugins.decorators import cache_result, plugin, requires

# from pdf_autofillr_plugins.interfaces import (
#     ChunkerPlugin, EmbedderPlugin, FillerPlugin, TransformerPlugin,
#     ValidatorPlugin, ExtractorPlugin, MapperPlugin, PluginMetadata,
# )
from pdf_autofillr_plugins.interfaces import (
    ChunkerPlugin,
    EmbedderPlugin,
    FillerPlugin,
    PluginMetadata,
    TransformerPlugin,
    ValidatorPlugin,
)
from pdf_autofillr_plugins.utils import (
    Timer,
    chunk_list,
    format_bytes,
    generate_content_hash,
    generate_session_id,
    get_file_extension,
    merge_dicts,
    retry_with_backoff,
    safe_json_dumps,
    safe_json_loads,
    sanitize_filename,
    truncate_string,
)

# from pdf_autofillr_plugins.interfaces.base_plugin import BasePlugin


# ── Utils ────────────────────────────────────────────────────────────────────


class TestTimer:
    def test_measures_elapsed_time(self):
        with Timer("test") as t:
            time.sleep(0.01)
        assert t.duration is not None
        assert t.duration >= 0.01

    def test_get_duration_ms(self):
        with Timer() as t:
            pass
        assert t.get_duration_ms() >= 0

    def test_duration_none_before_exit(self):
        t = Timer()
        assert t.duration is None


class TestSafeJson:
    def test_dumps_basic(self):
        result = safe_json_dumps({"key": "value"})
        assert json.loads(result) == {"key": "value"}

    def test_dumps_datetime(self):
        from datetime import datetime

        result = safe_json_dumps({"ts": datetime(2026, 1, 1)})
        assert "2026-01-01" in result

    def test_dumps_unknown_type(self):
        class Foo:
            pass

        result = safe_json_dumps({"obj": Foo()})
        assert result  # should not raise

    def test_loads_valid(self):
        result = safe_json_loads('{"a": 1}')
        assert result == {"a": 1}

    def test_loads_invalid_returns_default(self):
        result = safe_json_loads("not json", default={"err": True})
        assert result == {"err": True}

    def test_loads_invalid_returns_none_by_default(self):
        result = safe_json_loads("bad json")
        assert result is None


class TestStringHelpers:
    def test_sanitize_filename(self):
        assert sanitize_filename('file<>:"/\\|?*.txt') == "file_________.txt"

    def test_sanitize_filename_strips_leading_dots(self):
        result = sanitize_filename("...hidden")
        assert not result.startswith(".")

    def test_sanitize_filename_truncates(self):
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_truncate_string_short(self):
        assert truncate_string("hello", 100) == "hello"

    def test_truncate_string_long(self):
        result = truncate_string("a" * 200, 10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_format_bytes(self):
        assert "B" in format_bytes(100)
        assert "KB" in format_bytes(2048)
        assert "MB" in format_bytes(2 * 1024 * 1024)

    def test_get_file_extension(self):
        assert get_file_extension("document.pdf") == ".pdf"
        assert get_file_extension("noext") == ""

    def test_chunk_list(self):
        chunks = chunk_list([1, 2, 3, 4, 5], 2)
        assert chunks == [[1, 2], [3, 4], [5]]

    def test_chunk_list_empty(self):
        assert chunk_list([], 3) == []

    def test_merge_dicts(self):
        result = merge_dicts({"a": 1}, {"b": 2}, {"a": 99})
        assert result == {"a": 99, "b": 2}

    def test_merge_dicts_none_ignored(self):
        result = merge_dicts({"a": 1}, None, {"b": 2})
        assert result == {"a": 1, "b": 2}


class TestHashing:
    def test_generate_session_id_unique(self):
        ids = {generate_session_id() for _ in range(10)}
        assert len(ids) == 10

    def test_generate_content_hash(self):
        h1 = generate_content_hash(b"hello")
        h2 = generate_content_hash(b"hello")
        h3 = generate_content_hash(b"world")
        assert h1 == h2
        assert h1 != h3
        assert len(h1) == 64  # sha256 hex

    def test_generate_content_hash_md5(self):
        h = generate_content_hash(b"test", algorithm="md5")
        assert len(h) == 32


class TestRetry:
    def test_succeeds_first_try(self):
        result = retry_with_backoff(lambda: 42, max_retries=3)
        assert result == 42

    def test_retries_on_exception(self):
        call_count = [0]

        def flaky():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("not yet")
            return "ok"

        result = retry_with_backoff(flaky, max_retries=3, initial_delay=0.001)
        assert result == "ok"
        assert call_count[0] == 3

    def test_raises_after_max_retries(self):
        with pytest.raises(RuntimeError):
            retry_with_backoff(
                lambda: (_ for _ in ()).throw(RuntimeError("always fails")),
                max_retries=2,
                initial_delay=0.001,
            )


# ── Decorators ───────────────────────────────────────────────────────────────


class TestRequiresDecorator:
    def test_sets_dependencies_attribute(self):
        @requires("numpy", "pandas")
        class MyPlugin:
            pass

        assert MyPlugin._plugin_dependencies == ["numpy", "pandas"]

    def test_empty_dependencies(self):
        @requires()
        class NoDepPlugin:
            pass

        assert NoDepPlugin._plugin_dependencies == []


class TestCacheResultDecorator:
    def test_caches_return_value(self):
        call_count = [0]

        @plugin(category="validator", name="cache-test-plugin")
        class CachePlugin(ValidatorPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="cache-test-plugin",
                    version="1.0",
                    author="T",
                    description="",
                    category="validator",
                )

            def supports_field_type(self, ft):
                return True

            def validate(self, name, value, rules=None, **kw):
                return {
                    "valid": True,
                    "errors": [],
                    "warnings": [],
                    "validator": "cache-test-plugin",
                }

            @cache_result(ttl=60)
            def expensive_op(self, x):
                call_count[0] += 1
                return x * 2

        p = CachePlugin()
        assert p.expensive_op(5) == 10
        assert p.expensive_op(5) == 10  # cached
        assert call_count[0] == 1  # only called once


# ── Plugin interfaces — abstract method coverage ──────────────────────────────


class TestChunkerInterface:
    def test_default_chunk_size(self):
        @plugin(category="chunker", name="test-chunker")
        class TestChunker(ChunkerPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test-chunker",
                    version="1.0",
                    author="T",
                    description="",
                    category="chunker",
                )

            def chunk(self, pdf_path, chunk_size=None, **kw):
                return [{"chunk_id": "1", "content": "text", "page_numbers": [1], "metadata": {}}]

        c = TestChunker()
        c.initialize()
        assert c.get_optimal_chunk_size("any.pdf") == 1000
        assert c.supports_chunking_strategy("page") is True
        assert c.supports_chunking_strategy("unknown") is False
        chunks = c.chunk("form.pdf")
        assert len(chunks) == 1
        assert chunks[0]["chunk_id"] == "1"

    def test_chunker_metadata_defaults(self):
        @plugin(category="chunker", name="test-chunker-2")
        class TestChunker2(ChunkerPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test-chunker-2",
                    version="1.0",
                    author="T",
                    description="",
                    category="chunker",
                )

            def chunk(self, pdf_path, chunk_size=None, **kw):
                return []

        c = TestChunker2()
        assert c.name == "test-chunker-2"
        assert c.category == "chunker"


class TestEmbedderInterface:
    def test_embed_and_check(self):
        @plugin(category="embedder", name="test-embedder")
        class TestEmbedder(EmbedderPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test-embedder",
                    version="1.0",
                    author="T",
                    description="",
                    category="embedder",
                )

            def embed(self, pdf_path, metadata, output_path=None, **kw):
                return {
                    "output_path": output_path or "out.pdf",
                    "embedded_keys": list(metadata.keys()),
                    "embedder": "test-embedder",
                }

            def check(self, pdf_path, **kw):
                return {"has_metadata": True, "metadata": {}, "embedded_keys": []}

        e = TestEmbedder()
        e.initialize()
        result = e.embed("form.pdf", {"key1": "val1"}, "form_embedded.pdf")
        assert result["embedded_keys"] == ["key1"]
        assert e.check("form.pdf")["has_metadata"] is True
        assert e.supports_format("custom") is True
        assert e.supports_format("xmp") is False


class TestFillerInterface:
    def test_fill_returns_correct_keys(self):
        @plugin(category="filler", name="test-filler")
        class TestFiller(FillerPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test-filler", version="1.0", author="T", description="", category="filler"
                )

            def supports_pdf_type(self, pdf_path):
                return True

            def fill(self, pdf_path, data, output_path=None, **kw):
                return {
                    "output_path": output_path or "filled.pdf",
                    "filled_fields": list(data.keys()),
                    "unfilled_fields": [],
                    "filler": "test-filler",
                }

        f = TestFiller()
        f.initialize()
        result = f.fill("form.pdf", {"name": "Jane", "email": "jane@example.com"})
        assert result["filled_fields"] == ["name", "email"]
        assert result["unfilled_fields"] == []
        assert f.supports_pdf_type("any.pdf") is True
        assert f.get_fillable_fields("any.pdf") == []
        val = f.validate_data("form.pdf", {"name": "Jane"})
        assert val["valid"] is True


class TestTransformerInterface:
    def test_transform_and_reverse(self):
        @plugin(category="transformer", name="test-transformer")
        class UpperCaseTransformer(TransformerPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test-transformer",
                    version="1.0",
                    author="T",
                    description="",
                    category="transformer",
                )

            def supports_type(self, value_type):
                return value_type in {str}

            def transform(self, value, transform_type=None, **kw):
                return str(value).upper()

        t = UpperCaseTransformer()
        t.initialize()
        assert t.transform("hello") == "HELLO"
        assert t.supports_type(str) is True
        assert t.supports_type(int) is False
        assert t.can_reverse() is False
        assert "default" in t.get_supported_transformations()
        with pytest.raises(NotImplementedError):
            t.reverse("HELLO")


class TestValidatorBatchMethod:
    def test_validate_batch(self):
        from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

        v = EmailValidatorPlugin()
        v.initialize()
        fields = {
            "email1": "user@example.com",
            "email2": "bad-email",
        }
        results = v.validate_batch(fields)
        assert results["email1"]["valid"] is True
        assert results["email2"]["valid"] is False


class TestExtractorDefaults:
    def test_validate_pdf_default_true(self):
        from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import (
            PassthroughExtractorPlugin,
        )

        e = PassthroughExtractorPlugin(config={"fields": []})
        e.initialize()
        assert e.validate_pdf("any.pdf") is True

    def test_get_supported_strategies_passthrough(self):
        from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import (
            PassthroughExtractorPlugin,
        )

        e = PassthroughExtractorPlugin()
        assert "passthrough" in e.get_supported_strategies()


class TestMapperDefaults:
    def test_validate_mapping_default_true(self):
        from pdf_autofillr_plugins.builtin.mappers.identity_mapper import IdentityMapperPlugin

        m = IdentityMapperPlugin()
        m.initialize()
        assert m.validate_mapping({"field": "val"}, {"field": "string"}) is True


class TestBasePluginReprStr:
    def test_repr(self):
        from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

        v = EmailValidatorPlugin()
        r = repr(v)
        assert "EmailValidatorPlugin" in r
        assert "email-validator" in r

    def test_str(self):
        from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

        v = EmailValidatorPlugin()
        s = str(v)
        assert "email-validator" in s
        assert "1.0.0" in s

    def test_is_initialized_false_before_init(self):
        from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

        v = EmailValidatorPlugin()
        assert v.is_initialized is False

    def test_is_initialized_true_after_init(self):
        from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

        v = EmailValidatorPlugin()
        v.initialize()
        assert v.is_initialized is True

    def test_priority_property(self):
        from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import (
            InvoiceExtractorPlugin,
        )

        e = InvoiceExtractorPlugin()
        assert e.priority == 200

    def test_tags_property(self):
        from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import (
            InvoiceExtractorPlugin,
        )

        e = InvoiceExtractorPlugin()
        assert "invoice" in e.tags

    def test_get_config_value_default(self):
        from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

        v = EmailValidatorPlugin()
        assert v.get_config_value("nonexistent_key", "fallback") == "fallback"

    def test_validate_config_default_true(self):
        from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

        v = EmailValidatorPlugin()
        assert v.validate_config({"any": "config"}) is True
