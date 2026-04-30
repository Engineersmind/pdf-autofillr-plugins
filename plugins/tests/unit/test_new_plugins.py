"""Unit tests for InvoiceExtractorPlugin, MLMapperPlugin, and utils.common."""
import pytest
from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import InvoiceExtractorPlugin
from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin, _DEFAULT_SYNONYMS
from pdf_autofillr_plugins.utils.common import (
    Timer,
    chunk_list,
    format_bytes,
    generate_content_hash,
    generate_session_id,
    merge_dicts,
    retry_with_backoff,
    safe_json_dumps,
    safe_json_loads,
    sanitize_filename,
    truncate_string,
)


# ── InvoiceExtractorPlugin ────────────────────────────────────────────────────

class TestInvoiceExtractorPlugin:
    @pytest.fixture
    def extractor(self):
        e = InvoiceExtractorPlugin()
        e.initialize()
        return e

    def test_supports_invoice_filename(self, extractor):
        assert extractor.supports("q1_invoice.pdf") is True
        assert extractor.supports("INVOICE_2026.pdf") is True

    def test_does_not_support_non_invoice(self, extractor):
        assert extractor.supports("blank_form.pdf") is False
        assert extractor.supports("lp_subscription.pdf") is False

    def test_extract_returns_four_fields(self, extractor):
        result = extractor.extract("sample_invoice.pdf")
        assert len(result["fields"]) == 4

    def test_extract_field_names(self, extractor):
        result = extractor.extract("sample_invoice.pdf")
        names = {f["name"] for f in result["fields"]}
        assert names == {"invoice_number", "invoice_date", "vendor_name", "total_amount"}

    def test_extract_confidence_high(self, extractor):
        result = extractor.extract("sample_invoice.pdf")
        assert result["confidence"] >= 0.9
        for f in result["fields"]:
            assert f["confidence"] >= 0.9

    def test_extract_metadata_contains_pdf_path(self, extractor):
        result = extractor.extract("my_invoice.pdf")
        assert result["metadata"]["pdf_path"] == "my_invoice.pdf"
        assert result["metadata"]["document_type"] == "invoice"

    def test_extractor_name(self, extractor):
        assert extractor.name == "invoice-extractor"
        assert extractor.category == "extractor"

    def test_supported_strategies(self, extractor):
        strategies = extractor.get_supported_strategies()
        assert "template" in strategies
        assert "ml" in strategies

    def test_config_overrides_defaults(self):
        e = InvoiceExtractorPlugin(config={"default_vendor_name": "ACME Ltd"})
        e.initialize()
        result = e.extract("invoice.pdf")
        vendor = next(f for f in result["fields"] if f["name"] == "vendor_name")
        assert vendor["value"] == "ACME Ltd"

    def test_metadata(self, extractor):
        meta = extractor.get_metadata()
        assert meta.name == "invoice-extractor"
        assert meta.version == "1.0.0"
        assert "invoice" in meta.tags


# ── MLMapperPlugin ────────────────────────────────────────────────────────────

class TestMLMapperPlugin:
    @pytest.fixture
    def mapper(self):
        m = MLMapperPlugin()
        m.initialize()
        return m

    def test_maps_via_synonym_table(self, mapper):
        fields = [{"name": "first_name", "value": "Jane", "confidence": 1.0}]
        result = mapper.map_fields(fields)
        assert result["mapped_fields"].get("firstName") == "Jane"

    def test_maps_normalised_variant(self, mapper):
        fields = [{"name": "Email Address", "value": "j@e.com", "confidence": 1.0}]
        result = mapper.map_fields(fields)
        assert "emailAddress" in result["mapped_fields"]

    def test_unmapped_when_no_match(self, mapper):
        fields = [{"name": "completely_unknown_field_xyz", "value": "x", "confidence": 1.0}]
        result = mapper.map_fields(fields)
        assert "completely_unknown_field_xyz" in result["unmapped_fields"]

    def test_maps_directly_from_schema_key(self, mapper):
        fields = [{"name": "my_custom_key", "value": "v", "confidence": 1.0}]
        schema = {"my_custom_key": "string"}
        result = mapper.map_fields(fields, schema)
        assert result["mapped_fields"].get("my_custom_key") == "v"

    def test_coverage_metric(self, mapper):
        fields = [
            {"name": "first_name", "value": "A", "confidence": 1.0},
            {"name": "xyz_unknown", "value": "B", "confidence": 1.0},
        ]
        result = mapper.map_fields(fields)
        assert result["coverage"] == pytest.approx(0.5)

    def test_empty_fields(self, mapper):
        result = mapper.map_fields([])
        assert result["mapped_fields"] == {}
        assert result["coverage"] == 0.0

    def test_supports_any_schema(self, mapper):
        assert mapper.supports_schema({}) is True
        assert mapper.supports_schema({"a": "b"}) is True

    def test_custom_synonyms_via_config(self):
        m = MLMapperPlugin(config={"synonyms": {"my_source": "myTarget"}})
        m.initialize()
        fields = [{"name": "my_source", "value": "v", "confidence": 1.0}]
        result = m.map_fields(fields)
        assert result["mapped_fields"].get("myTarget") == "v"

    def test_invoice_fields_mapped(self, mapper):
        fields = [
            {"name": "invoice_number", "value": "INV-001", "confidence": 1.0},
            {"name": "total_amount",   "value": "999.00",  "confidence": 1.0},
            {"name": "vendor_name",    "value": "ACME",    "confidence": 1.0},
        ]
        result = mapper.map_fields(fields)
        assert "invoiceNo"    in result["mapped_fields"]
        assert "totalAmount"  in result["mapped_fields"]
        assert "vendorName"   in result["mapped_fields"]

    def test_metadata(self, mapper):
        assert mapper.name == "ml-mapper"
        assert mapper.category == "mapper"

    def test_default_synonyms_not_empty(self):
        assert len(_DEFAULT_SYNONYMS) > 10


# ── utils.common ──────────────────────────────────────────────────────────────

class TestCommonUtils:
    def test_generate_session_id_unique(self):
        ids = {generate_session_id() for _ in range(100)}
        assert len(ids) == 100

    def test_generate_content_hash_sha256(self):
        h = generate_content_hash(b"hello")
        assert len(h) == 64  # sha256 hex digest

    def test_generate_content_hash_md5(self):
        h = generate_content_hash(b"hello", algorithm="md5")
        assert len(h) == 32

    def test_safe_json_dumps_datetime(self):
        from datetime import datetime
        d = datetime(2026, 4, 30, 12, 0, 0)
        result = safe_json_dumps({"ts": d})
        assert "2026-04-30" in result

    def test_safe_json_dumps_plain(self):
        result = safe_json_dumps({"a": 1})
        assert result == '{"a": 1}'

    def test_safe_json_loads_valid(self):
        assert safe_json_loads('{"a": 1}') == {"a": 1}

    def test_safe_json_loads_invalid_returns_default(self):
        assert safe_json_loads("not json") is None
        assert safe_json_loads("not json", default={}) == {}

    def test_merge_dicts(self):
        result = merge_dicts({"a": 1}, {"b": 2}, {"a": 99})
        assert result == {"a": 99, "b": 2}

    def test_merge_dicts_skips_none(self):
        result = merge_dicts({"a": 1}, None, {"b": 2})  # type: ignore[arg-type]
        assert result == {"a": 1, "b": 2}

    def test_sanitize_filename(self):
        assert sanitize_filename('my/file:name?.pdf') == 'my_file_name_.pdf'

    def test_sanitize_filename_strips_dots(self):
        assert sanitize_filename('...file...') == 'file'

    def test_format_bytes(self):
        assert format_bytes(0) == "0.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"

    def test_truncate_string_short(self):
        assert truncate_string("hi", 10) == "hi"

    def test_truncate_string_long(self):
        result = truncate_string("hello world", 8)
        assert len(result) == 8
        assert result.endswith("...")

    def test_chunk_list(self):
        chunks = chunk_list([1, 2, 3, 4, 5], 2)
        assert chunks == [[1, 2], [3, 4], [5]]

    def test_chunk_list_empty(self):
        assert chunk_list([], 3) == []

    def test_retry_with_backoff_success_first_try(self):
        calls = []
        def fn():
            calls.append(1)
            return "ok"
        assert retry_with_backoff(fn, max_retries=3, initial_delay=0) == "ok"
        assert len(calls) == 1

    def test_retry_with_backoff_succeeds_after_retries(self):
        calls = []
        def fn():
            calls.append(1)
            if len(calls) < 3:
                raise ValueError("not yet")
            return "done"
        result = retry_with_backoff(fn, max_retries=5, initial_delay=0)
        assert result == "done"
        assert len(calls) == 3

    def test_retry_with_backoff_raises_after_max(self):
        def fn():
            raise RuntimeError("always fails")
        with pytest.raises(RuntimeError):
            retry_with_backoff(fn, max_retries=2, initial_delay=0)

    def test_timer_measures_time(self):
        import time as _time
        with Timer("test") as t:
            _time.sleep(0.01)
        assert t.duration is not None
        assert t.duration >= 0.01
        assert t.get_duration_ms() >= 10
