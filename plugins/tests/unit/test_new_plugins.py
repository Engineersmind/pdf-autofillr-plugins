"""Unit tests for MLMapperPlugin, InvoiceExtractorPlugin, and CLI commands."""

import pytest

from pdf_autofillr_plugins.builtin.extractors.invoice_extractor import (
    InvoiceExtractorPlugin,
)
from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin

# ── MLMapperPlugin ────────────────────────────────────────────────────────────


class TestMLMapperPlugin:
    @pytest.fixture
    def mapper(self):
        m = MLMapperPlugin()
        m.initialize()
        return m

    def test_synonym_exact_match(self, mapper):
        fields = [{"name": "first_name", "value": "Jane", "confidence": 0.9}]
        result = mapper.map_fields(fields)
        assert result["mapped_fields"].get("firstName") == "Jane"

    def test_synonym_normalised_match(self, mapper):
        fields = [{"name": "email address", "value": "jane@example.com", "confidence": 0.9}]
        result = mapper.map_fields(fields)
        # "email address" normalises to "email_address" which maps to "emailAddress"
        assert "emailAddress" in result["mapped_fields"]

    def test_unmapped_field(self, mapper):
        fields = [{"name": "completely_unknown_field", "value": "x", "confidence": 0.9}]
        result = mapper.map_fields(fields)
        assert "completely_unknown_field" in result["unmapped_fields"]

    def test_empty_fields(self, mapper):
        result = mapper.map_fields([])
        assert result["mapped_fields"] == {}
        assert result["coverage"] == 0.0

    def test_supports_any_schema(self, mapper):
        assert mapper.supports_schema({}) is True
        assert mapper.supports_schema({"key": "val"}) is True

    def test_custom_synonyms_via_config(self):
        m = MLMapperPlugin(config={"synonyms": {"my_custom_field": "canonicalKey"}})
        m.initialize()
        fields = [{"name": "my_custom_field", "value": "test", "confidence": 0.9}]
        result = m.map_fields(fields)
        assert result["mapped_fields"].get("canonicalKey") == "test"

    def test_metadata(self, mapper):
        assert mapper.name == "ml-mapper"
        assert mapper.category == "mapper"
        assert mapper.version == "1.0.0"

    def test_confidence_score(self, mapper):
        fields = [{"name": "first_name", "value": "Jane", "confidence": 0.9}]
        result = mapper.map_fields(fields)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_coverage_metric(self, mapper):
        fields = [
            {"name": "first_name", "value": "Jane", "confidence": 0.9},
            {"name": "completely_unknown", "value": "x", "confidence": 0.5},
        ]
        result = mapper.map_fields(fields)
        assert result["coverage"] == pytest.approx(0.5)


# ── InvoiceExtractorPlugin ────────────────────────────────────────────────────


class TestInvoiceExtractorPlugin:
    @pytest.fixture
    def extractor(self):
        e = InvoiceExtractorPlugin()
        e.initialize()
        return e

    def test_supports_invoice_path(self, extractor):
        assert extractor.supports("q1_invoice.pdf") is True
        assert extractor.supports("INVOICE_2026.pdf") is True

    def test_does_not_support_non_invoice(self, extractor):
        assert extractor.supports("blank_form.pdf") is False

    def test_extract_returns_four_fields(self, extractor):
        result = extractor.extract("invoice_test.pdf")
        assert len(result["fields"]) == 4
        field_names = {f["name"] for f in result["fields"]}
        assert {
            "invoice_number",
            "invoice_date",
            "vendor_name",
            "total_amount",
        } == field_names

    def test_extractor_name_in_result(self, extractor):
        result = extractor.extract("invoice.pdf")
        assert result["extractor"] == "invoice-extractor"

    def test_confidence_above_threshold(self, extractor):
        result = extractor.extract("invoice.pdf")
        for f in result["fields"]:
            assert f["confidence"] >= 0.9

    def test_custom_defaults_via_config(self):
        e = InvoiceExtractorPlugin(config={"default_vendor_name": "My Corp"})
        e.initialize()
        result = e.extract("invoice.pdf")
        vendor = next(f for f in result["fields"] if f["name"] == "vendor_name")
        assert vendor["value"] == "My Corp"

    def test_supported_strategies(self, extractor):
        strategies = extractor.get_supported_strategies()
        assert "template" in strategies
        assert "ml" in strategies

    def test_metadata(self, extractor):
        assert extractor.name == "invoice-extractor"
        assert extractor.category == "extractor"
        assert extractor.priority == 200

    def test_metadata_contains_pdf_path(self, extractor):
        result = extractor.extract("my_invoice.pdf")
        assert result["metadata"]["pdf_path"] == "my_invoice.pdf"
        assert result["metadata"]["document_type"] == "invoice"


# ── CLI entry point ───────────────────────────────────────────────────────────


class TestCLI:
    def test_version_import(self):
        from pdf_autofillr_plugins import __version__

        assert __version__ == "0.2.0"

    def test_cli_module_importable(self):
        from pdf_autofillr_plugins.cli import build_parser

        parser = build_parser()
        assert parser is not None

    def test_cli_has_setup_subcommand(self):
        from pdf_autofillr_plugins.cli import build_parser

        parser = build_parser()
        # Parse setup — should not raise
        args = parser.parse_args(["setup"])
        assert args.command == "setup"

    def test_cli_has_status_subcommand(self):
        from pdf_autofillr_plugins.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["status"])
        assert args.command == "status"

    def test_cli_has_list_subcommand(self):
        from pdf_autofillr_plugins.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["list", "--path", "./my_plugins"])
        assert args.command == "list"
        assert args.path == "./my_plugins"
