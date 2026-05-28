"""Unit tests for built-in plugins: EmailValidator, PassthroughExtractor, IdentityMapper."""

import pytest

from pdf_autofillr_plugins.builtin.extractors.passthrough_extractor import (
    PassthroughExtractorPlugin,
)
from pdf_autofillr_plugins.builtin.mappers.identity_mapper import (
    IdentityMapperPlugin,
    _to_snake,
)
from pdf_autofillr_plugins.builtin.validators.email_validator import (
    EmailValidatorPlugin,
)

# ── EmailValidatorPlugin ──────────────────────────────────────────────────────


class TestEmailValidatorPlugin:
    @pytest.fixture
    def validator(self):
        v = EmailValidatorPlugin()
        v.initialize()
        return v

    def test_valid_email(self, validator):
        r = validator.validate("email", "user@example.com")
        assert r["valid"] is True
        assert r["errors"] == []

    def test_invalid_format(self, validator):
        r = validator.validate("email", "not-an-email")
        assert r["valid"] is False
        assert len(r["errors"]) > 0

    def test_missing_at_sign(self, validator):
        r = validator.validate("email", "nodomain")
        assert r["valid"] is False

    def test_non_string_value(self, validator):
        r = validator.validate("email", 12345)
        assert r["valid"] is False
        assert "string" in r["errors"][0].lower()

    def test_too_long_email(self, validator):
        long_email = "a" * 250 + "@example.com"
        r = validator.validate("email", long_email)
        assert r["valid"] is False
        assert any("254" in e for e in r["errors"])

    def test_disposable_domain_warning(self, validator):
        r = validator.validate("email", "test@tempmail.com")
        assert r["valid"] is True  # warnings don't fail
        assert len(r["warnings"]) > 0
        assert r["warnings"][0] == "Disposable email domain detected: tempmail.com"

    def test_allowed_domains_rule(self, validator):
        r = validator.validate(
            "email", "user@gmail.com", rules={"allowed_domains": ["company.com"]}
        )
        assert r["valid"] is False

    def test_require_corporate_rule(self, validator):
        r = validator.validate("email", "user@gmail.com", rules={"require_corporate": True})
        assert r["valid"] is True  # still valid
        assert len(r["warnings"]) > 0  # but warned

    def test_supports_email_field_types(self, validator):
        for ft in ["email", "email_address", "emailaddress", "e-mail"]:
            assert validator.supports_field_type(ft) is True

    def test_does_not_support_phone_type(self, validator):
        assert validator.supports_field_type("phone") is False

    def test_metadata(self, validator):
        assert validator.name == "email-validator"
        assert validator.version == "1.0.0"
        assert validator.category == "validator"

    def test_get_validation_rules(self, validator):
        rules = validator.get_validation_rules()
        assert "require_corporate" in rules
        assert "allowed_domains" in rules


# ── PassthroughExtractorPlugin ────────────────────────────────────────────────


class TestPassthroughExtractorPlugin:
    @pytest.fixture
    def extractor_with_fields(self):
        fields = [
            {"name": "investor_name", "value": "Jane Smith", "confidence": 0.99},
            {"name": "email", "value": "jane@example.com", "confidence": 0.98},
        ]
        e = PassthroughExtractorPlugin(config={"fields": fields})
        e.initialize()
        return e, fields

    @pytest.fixture
    def empty_extractor(self):
        e = PassthroughExtractorPlugin()
        e.initialize()
        return e

    def test_extract_returns_configured_fields(self, extractor_with_fields):
        extractor, fields = extractor_with_fields
        result = extractor.extract("dummy.pdf")
        assert result["fields"] == fields
        assert result["extractor"] == "passthrough-extractor"

    def test_supports_when_fields_configured(self, extractor_with_fields):
        extractor, _ = extractor_with_fields
        assert extractor.supports("any.pdf") is True

    def test_supports_false_when_no_fields(self, empty_extractor):
        assert empty_extractor.supports("any.pdf") is False

    def test_extract_empty_fields(self, empty_extractor):
        result = empty_extractor.extract("dummy.pdf")
        assert result["fields"] == []

    def test_metadata(self, empty_extractor):
        assert empty_extractor.name == "passthrough-extractor"
        assert empty_extractor.category == "extractor"

    def test_supported_strategies(self, empty_extractor):
        assert "passthrough" in empty_extractor.get_supported_strategies()

    def test_pdf_path_reflected_in_metadata(self, extractor_with_fields):
        extractor, _ = extractor_with_fields
        result = extractor.extract("my_form.pdf")
        assert result["metadata"]["pdf_path"] == "my_form.pdf"


# ── IdentityMapperPlugin ──────────────────────────────────────────────────────


class TestIdentityMapperPlugin:
    @pytest.fixture
    def mapper(self):
        m = IdentityMapperPlugin()
        m.initialize()
        return m

    def test_exact_match(self, mapper):
        fields = [{"name": "investor_name", "value": "Jane", "confidence": 1.0}]
        schema = {"investor_name": "string"}
        result = mapper.map_fields(fields, schema)
        assert result["mapped_fields"]["investor_name"] == "Jane"
        assert "investor_name" not in result["unmapped_fields"]

    def test_snake_case_match(self, mapper):
        fields = [{"name": "Investor Name", "value": "Jane", "confidence": 1.0}]
        schema = {"investor_name": "string"}
        result = mapper.map_fields(fields, schema)
        assert result["mapped_fields"].get("investor_name") == "Jane"

    def test_unmapped_field(self, mapper):
        fields = [{"name": "unknown_field", "value": "x", "confidence": 1.0}]
        schema = {"investor_name": "string"}
        result = mapper.map_fields(fields, schema)
        assert "unknown_field" in result["unmapped_fields"]

    def test_passthrough_when_no_schema(self, mapper):
        fields = [{"name": "foo", "value": "bar", "confidence": 1.0}]
        result = mapper.map_fields(fields, target_schema=None)
        assert result["mapped_fields"]["foo"] == "bar"

    def test_empty_fields(self, mapper):
        result = mapper.map_fields([], {})
        assert result["mapped_fields"] == {}
        assert result["coverage"] == 0.0

    def test_coverage_metric(self, mapper):
        fields = [
            {"name": "a", "value": "1", "confidence": 1.0},
            {"name": "b", "value": "2", "confidence": 1.0},
        ]
        schema = {"a": "str"}  # only 'a' matches
        result = mapper.map_fields(fields, schema)
        assert result["coverage"] == pytest.approx(0.5)

    def test_supports_any_schema(self, mapper):
        assert mapper.supports_schema({}) is True
        assert mapper.supports_schema({"anything": "goes"}) is True

    def test_metadata(self, mapper):
        assert mapper.name == "identity-mapper"
        assert mapper.category == "mapper"

    def test_get_mapping_confidence(self, mapper):
        fields = [{"name": "investor_name", "value": "Jane", "confidence": 1.0}]
        conf = mapper.get_mapping_confidence(fields, {"investor_name": "str"})
        assert 0.0 <= conf <= 1.0


class TestToSnake:
    def test_spaces_to_underscore(self):
        assert _to_snake("Investor Name") == "investor_name"

    def test_hyphens_to_underscore(self):
        assert _to_snake("first-name") == "first_name"

    def test_already_snake(self):
        assert _to_snake("investor_name") == "investor_name"

    def test_mixed_case(self):
        assert _to_snake("InvestorName") == "investorname"

    def test_strips_special_chars(self):
        assert _to_snake("field!@#name") == "fieldname"
