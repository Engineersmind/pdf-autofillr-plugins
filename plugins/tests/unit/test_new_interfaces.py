"""
Unit tests for the three new plugin interfaces and their built-ins:
  - LLMAdapter (flagship — Sir's vision)
  - OutputFormatterPlugin
  - DataConnectorPlugin

And PluginManager.find_llm_adapter / find_output_formatter / find_data_connector.
"""

from __future__ import annotations

import json

# import tempfile
# import os
import pytest

from pdf_autofillr_plugins import PluginManager, plugin
from pdf_autofillr_plugins.builtin.data_connectors.dict_connector import DictConnector
from pdf_autofillr_plugins.builtin.data_connectors.json_file_connector import (
    JSONFileConnector,
)
from pdf_autofillr_plugins.builtin.llm_adapters.litellm_adapter import LiteLLMAdapter
from pdf_autofillr_plugins.builtin.llm_adapters.noop_llm_adapter import NoOpLLMAdapter
from pdf_autofillr_plugins.builtin.output_formatters.json_report_formatter import (
    JSONReportFormatter,
)
from pdf_autofillr_plugins.builtin.output_formatters.passthrough_formatter import (
    PassthroughFormatter,
)
from pdf_autofillr_plugins.interfaces import (
    DataConnectorPlugin,
    LLMAdapter,
    OutputFormatterPlugin,
    PluginMetadata,
)

# ── LLMAdapter interface ──────────────────────────────────────────────────────


class TestLLMAdapterInterface:
    """Tests for the LLMAdapter abstract interface."""

    def test_can_instantiate_concrete_subclass(self):
        @plugin(category="llm_adapter", name="test-llm")
        class TestLLM(LLMAdapter):
            def get_metadata(self):
                return PluginMetadata(
                    name="test-llm",
                    version="1.0",
                    author="T",
                    description="",
                    category="llm_adapter",
                )

            def map_fields(self, fields, context):
                return {f: f.upper() for f in fields}

            def embed(self, fields, schema_keys):
                return {f: {"schema_key": f, "confidence": 1.0} for f in fields}

        llm = TestLLM()
        llm.initialize()
        assert llm.name == "test-llm"
        assert llm.category == "llm_adapter"
        assert llm.is_initialized is True

    def test_map_fields_receives_fields_and_context(self):
        @plugin(category="llm_adapter", name="capture-llm")
        class CaptureLLM(LLMAdapter):
            received = {}

            def get_metadata(self):
                return PluginMetadata(
                    name="capture-llm",
                    version="1.0",
                    author="T",
                    description="",
                    category="llm_adapter",
                )

            def map_fields(self, fields, context):
                CaptureLLM.received = {"fields": fields, "context": context}
                return {f: f for f in fields}

            def embed(self, fields, schema_keys):
                return {}

        llm = CaptureLLM()
        llm.initialize()
        result = llm.map_fields(["investor_name", "email"], "LP form")
        assert CaptureLLM.received["fields"] == ["investor_name", "email"]
        assert CaptureLLM.received["context"] == "LP form"
        assert result == {"investor_name": "investor_name", "email": "email"}

    def test_embed_receives_fields_and_schema_keys(self):
        @plugin(category="llm_adapter", name="embed-llm")
        class EmbedLLM(LLMAdapter):
            def get_metadata(self):
                return PluginMetadata(
                    name="embed-llm",
                    version="1.0",
                    author="T",
                    description="",
                    category="llm_adapter",
                )

            def map_fields(self, fields, context):
                return {f: f for f in fields}

            def embed(self, fields, schema_keys):
                return {
                    f: {
                        "schema_key": schema_keys[i] if i < len(schema_keys) else f,
                        "confidence": 0.9,
                    }
                    for i, f in enumerate(fields)
                }

        llm = EmbedLLM()
        llm.initialize()
        result = llm.embed(["field_a", "field_b"], ["key_a", "key_b"])
        assert result["field_a"]["schema_key"] == "key_a"
        assert result["field_b"]["schema_key"] == "key_b"
        assert result["field_a"]["confidence"] == 0.9

    def test_default_supports_model_false(self):
        @plugin(category="llm_adapter", name="default-llm")
        class DefaultLLM(LLMAdapter):
            def get_metadata(self):
                return PluginMetadata(
                    name="default-llm",
                    version="1.0",
                    author="T",
                    description="",
                    category="llm_adapter",
                )

            def map_fields(self, fields, context):
                return {}

            def embed(self, fields, schema_keys):
                return {}

        llm = DefaultLLM()
        assert llm.supports_model("gpt-4o") is False
        assert llm.get_supported_models() == []

    def test_default_estimate_tokens(self):
        llm = NoOpLLMAdapter()
        tokens = llm.estimate_tokens(["field_a", "field_b"], "some context")
        assert tokens > 0


# ── NoOpLLMAdapter ────────────────────────────────────────────────────────────


class TestNoOpLLMAdapter:
    @pytest.fixture
    def adapter(self):
        a = NoOpLLMAdapter()
        a.initialize()
        return a

    def test_map_fields_passthrough(self, adapter):
        fields = ["investor_name", "email_address", "commitment_usd"]
        result = adapter.map_fields(fields, "LP form context")
        assert result == {
            "investor_name": "investor_name",
            "email_address": "email_address",
            "commitment_usd": "commitment_usd",
        }

    def test_map_fields_empty(self, adapter):
        assert adapter.map_fields([], "context") == {}

    def test_map_fields_with_override_mapping(self):
        a = NoOpLLMAdapter(config={"mapping": {"investor_name": "investor_full_name"}})
        a.initialize()
        result = a.map_fields(["investor_name", "email"], "context")
        assert result["investor_name"] == "investor_full_name"
        assert result["email"] == "email"  # not in override → passthrough

    def test_embed_positional_mapping(self, adapter):
        result = adapter.embed(["field_a", "field_b"], ["key_a", "key_b"])
        assert result["field_a"]["schema_key"] == "key_a"
        assert result["field_b"]["schema_key"] == "key_b"
        assert result["field_a"]["confidence"] == 1.0
        assert result["field_a"]["adapter"] == "noop-llm"

    def test_embed_more_fields_than_schema_keys(self, adapter):
        result = adapter.embed(["f1", "f2", "f3"], ["k1"])
        assert result["f1"]["schema_key"] == "k1"
        assert result["f2"]["schema_key"] == "f2"  # falls back to field name
        assert result["f3"]["schema_key"] == "f3"

    def test_embed_empty(self, adapter):
        assert adapter.embed([], []) == {}

    def test_supports_model_noop(self, adapter):
        assert adapter.supports_model("noop") is True
        assert adapter.supports_model("passthrough") is True
        assert adapter.supports_model("gpt-4o") is False

    def test_get_supported_models(self, adapter):
        models = adapter.get_supported_models()
        assert "noop" in models
        assert "passthrough" in models

    def test_metadata(self, adapter):
        assert adapter.name == "noop-llm"
        assert adapter.category == "llm_adapter"
        assert adapter.version == "1.0.0"

    def test_priority_is_low(self, adapter):
        assert adapter.priority == 1

    def test_tags(self, adapter):
        assert "testing" in adapter.tags
        assert "builtin" in adapter.tags


# ── LiteLLMAdapter (without real litellm) ────────────────────────────────────


class TestLiteLLMAdapterWithoutDep:
    """Test LiteLLMAdapter fallback behaviour when litellm is not installed."""

    def test_initializes_with_default_model(self):
        a = LiteLLMAdapter(config={"model": "openai/gpt-4o-mini"})
        a.initialize()
        assert a._model == "openai/gpt-4o-mini"

    def test_map_fields_falls_back_to_passthrough_on_import_error(self):
        """If litellm is not installed, map_fields should return passthrough."""
        import unittest.mock as mock

        a = LiteLLMAdapter(config={"model": "openai/gpt-4o-mini"})
        a.initialize()

        with mock.patch.dict("sys.modules", {"litellm": None}):
            result = a.map_fields(["field_a", "field_b"], "context")
        # Either passthrough or empty — must not raise
        assert isinstance(result, dict)

    def test_supports_model_any_string(self):
        a = LiteLLMAdapter()
        a.initialize()
        assert a.supports_model("gpt-4o") is True
        assert a.supports_model("claude-3-5-sonnet") is True
        assert a.supports_model("") is False

    def test_get_supported_models_list(self):
        a = LiteLLMAdapter()
        a.initialize()
        models = a.get_supported_models()
        assert "openai/gpt-4o" in models
        assert "anthropic/claude-3-5-haiku-latest" in models
        assert "ollama/llama3.2" in models

    def test_estimate_tokens_positive(self):
        a = LiteLLMAdapter()
        a.initialize()
        tokens = a.estimate_tokens(["investor_name", "email"], "LP subscription form")
        assert tokens > 0

    def test_metadata(self):
        a = LiteLLMAdapter()
        a.initialize()
        assert a.name == "litellm"
        assert a.category == "llm_adapter"

    def test_priority_is_100(self):
        a = LiteLLMAdapter()
        assert a.priority == 100


# ── OutputFormatterPlugin interface ───────────────────────────────────────────


class TestOutputFormatterInterface:
    def test_can_instantiate_concrete_subclass(self):
        @plugin(category="output_formatter", name="test-formatter")
        class TestFormatter(OutputFormatterPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test-formatter",
                    version="1.0",
                    author="T",
                    description="",
                    category="output_formatter",
                )

            def format(self, filled_pdf, field_map, **kwargs):
                return {"pdf": filled_pdf, "fields": field_map}

        f = TestFormatter()
        f.initialize()
        result = f.format(b"PDF_BYTES", {"name": "Jane"})
        assert result["pdf"] == b"PDF_BYTES"
        assert result["fields"] == {"name": "Jane"}

    def test_default_supports_format_false(self):
        @plugin(category="output_formatter", name="default-fmt")
        class DefaultFmt(OutputFormatterPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="default-fmt",
                    version="1.0",
                    author="T",
                    description="",
                    category="output_formatter",
                )

            def format(self, filled_pdf, field_map, **kwargs):
                return filled_pdf

        f = DefaultFmt()
        assert f.supports_format("json") is False
        assert f.get_supported_formats() == ["default"]


# ── JSONReportFormatter ───────────────────────────────────────────────────────


class TestJSONReportFormatter:
    @pytest.fixture
    def formatter(self):
        f = JSONReportFormatter()
        f.initialize()
        return f

    def test_format_returns_dict(self, formatter):
        result = formatter.format(b"PDF_BYTES", {"investor_name": "Jane"})
        assert isinstance(result, dict)

    def test_format_status_ok_when_no_unfilled(self, formatter):
        result = formatter.format(b"PDF", {"name": "Jane"})
        assert result["status"] == "ok"

    def test_format_status_partial_with_unfilled(self, formatter):
        result = formatter.format(
            b"PDF", {"name": "Jane"}, unfilled_fields=["email", "phone"]
        )
        assert result["status"] == "partial"
        assert result["unfilled_count"] == 2
        assert "email" in result["unfilled_fields"]

    def test_format_includes_report(self, formatter):
        field_map = {"investor_name": "Jane", "email": "jane@example.com"}
        result = formatter.format(b"PDF", field_map)
        assert result["report"] == field_map
        assert result["field_count"] == 2

    def test_format_includes_b64_pdf(self, formatter):
        import base64

        result = formatter.format(b"PDF_BYTES", {})
        assert "pdf_b64" in result
        assert base64.b64decode(result["pdf_b64"]) == b"PDF_BYTES"

    def test_format_includes_raw_bytes(self, formatter):
        result = formatter.format(b"PDF_BYTES", {})
        assert result["pdf_bytes"] == b"PDF_BYTES"

    def test_format_includes_timestamp(self, formatter):
        result = formatter.format(b"PDF", {})
        assert "timestamp" in result
        assert result["timestamp"].endswith("Z")

    def test_format_includes_session_and_user(self, formatter):
        result = formatter.format(b"PDF", {}, session_id="sess_001", user_id="user_abc")
        assert result["session_id"] == "sess_001"
        assert result["user_id"] == "user_abc"

    def test_format_includes_pdf_path(self, formatter):
        result = formatter.format(b"PDF", {}, pdf_path="/data/form.pdf")
        assert result["pdf_path"] == "/data/form.pdf"

    def test_format_formatter_key(self, formatter):
        result = formatter.format(b"PDF", {})
        assert result["formatter"] == "json-report"

    def test_config_disable_bytes(self):
        f = JSONReportFormatter(
            config={"include_pdf_bytes": False, "include_b64": False}
        )
        f.initialize()
        result = f.format(b"PDF", {})
        assert "pdf_bytes" not in result
        assert "pdf_b64" not in result

    def test_supports_format_json(self, formatter):
        assert formatter.supports_format("json") is True
        assert formatter.supports_format("json-report") is True
        assert formatter.supports_format("xml") is False

    def test_metadata(self, formatter):
        assert formatter.name == "json-report"
        assert formatter.category == "output_formatter"

    def test_priority_100(self, formatter):
        assert formatter.priority == 100


# ── PassthroughFormatter ──────────────────────────────────────────────────────


class TestPassthroughFormatter:
    @pytest.fixture
    def formatter(self):
        f = PassthroughFormatter()
        f.initialize()
        return f

    def test_format_returns_raw_bytes(self, formatter):
        result = formatter.format(b"RAW_PDF_BYTES", {"name": "Jane"})
        assert result == b"RAW_PDF_BYTES"

    def test_format_empty_bytes(self, formatter):
        result = formatter.format(b"", {})
        assert result == b""

    def test_supports_passthrough(self, formatter):
        assert formatter.supports_format("passthrough") is True
        assert formatter.supports_format("raw") is True
        assert formatter.supports_format("json") is False

    def test_metadata(self, formatter):
        assert formatter.name == "passthrough-formatter"
        assert formatter.category == "output_formatter"
        assert formatter.priority == 1


# ── DataConnectorPlugin interface ─────────────────────────────────────────────


class TestDataConnectorInterface:
    def test_can_instantiate_concrete_subclass(self):
        @plugin(category="data_connector", name="test-connector")
        class TestConnector(DataConnectorPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="test-connector",
                    version="1.0",
                    author="T",
                    description="",
                    category="data_connector",
                )

            def fetch(self, record_id, **kwargs):
                return {"investor_name": f"User {record_id}"}

        c = TestConnector()
        c.initialize()
        result = c.fetch("user_001")
        assert result["investor_name"] == "User user_001"

    def test_fetch_batch_default_calls_fetch(self):
        @plugin(category="data_connector", name="batch-connector")
        class BatchConnector(DataConnectorPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="batch-connector",
                    version="1.0",
                    author="T",
                    description="",
                    category="data_connector",
                )

            def fetch(self, record_id, **kwargs):
                return {"id": record_id}

        c = BatchConnector()
        c.initialize()
        results = c.fetch_batch(["r1", "r2", "r3"])
        assert results == {"r1": {"id": "r1"}, "r2": {"id": "r2"}, "r3": {"id": "r3"}}

    def test_default_supports_source_false(self):
        @plugin(category="data_connector", name="default-conn")
        class DefaultConn(DataConnectorPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="default-conn",
                    version="1.0",
                    author="T",
                    description="",
                    category="data_connector",
                )

            def fetch(self, record_id, **kwargs):
                return {}

        c = DefaultConn()
        assert c.supports_source("salesforce") is False
        assert c.get_supported_sources() == []
        assert c.test_connection() is True


# ── DictConnector ─────────────────────────────────────────────────────────────


class TestDictConnector:
    @pytest.fixture
    def connector(self):
        c = DictConnector(
            config={
                "data": {
                    "user_001": {
                        "investor_name": "Jane Smith",
                        "email": "jane@example.com",
                    },
                    "user_002": {
                        "investor_name": "John Doe",
                        "email": "john@example.com",
                    },
                }
            }
        )
        c.initialize()
        return c

    def test_fetch_existing_record(self, connector):
        result = connector.fetch("user_001")
        assert result == {"investor_name": "Jane Smith", "email": "jane@example.com"}

    def test_fetch_missing_record_returns_empty(self, connector):
        result = connector.fetch("nonexistent")
        assert result == {}

    def test_fetch_returns_copy_not_reference(self, connector):
        r1 = connector.fetch("user_001")
        r1["investor_name"] = "MODIFIED"
        r2 = connector.fetch("user_001")
        assert r2["investor_name"] == "Jane Smith"  # original unchanged

    def test_fetch_batch(self, connector):
        results = connector.fetch_batch(["user_001", "user_002"])
        assert results["user_001"]["investor_name"] == "Jane Smith"
        assert results["user_002"]["investor_name"] == "John Doe"

    def test_fetch_batch_partial_missing(self, connector):
        results = connector.fetch_batch(["user_001", "ghost"])
        assert results["user_001"]["investor_name"] == "Jane Smith"
        assert results["ghost"] == {}

    def test_supports_source(self, connector):
        assert connector.supports_source("dict") is True
        assert connector.supports_source("memory") is True
        assert connector.supports_source("salesforce") is False

    def test_test_connection(self, connector):
        assert connector.test_connection() is True

    def test_empty_config(self):
        c = DictConnector()
        c.initialize()
        assert c.fetch("anything") == {}

    def test_metadata(self, connector):
        assert connector.name == "dict-connector"
        assert connector.category == "data_connector"
        assert connector.version == "1.0.0"

    def test_priority_is_low(self, connector):
        assert connector.priority == 1

    def test_tags(self, connector):
        assert "testing" in connector.tags


# ── JSONFileConnector ─────────────────────────────────────────────────────────


class TestJSONFileConnector:
    @pytest.fixture
    def json_file(self, tmp_path):
        data = {
            "user_001": {"investor_name": "Jane Smith", "email": "jane@example.com"},
            "user_002": {"investor_name": "John Doe", "email": "john@example.com"},
        }
        f = tmp_path / "investors.json"
        f.write_text(json.dumps(data))
        return str(f)

    def test_fetch_from_file(self, json_file):
        c = JSONFileConnector(config={"file_path": json_file})
        c.initialize()
        result = c.fetch("user_001")
        assert result["investor_name"] == "Jane Smith"

    def test_fetch_missing_record(self, json_file):
        c = JSONFileConnector(config={"file_path": json_file})
        c.initialize()
        assert c.fetch("ghost") == {}

    def test_missing_file_returns_empty(self):
        c = JSONFileConnector(config={"file_path": "/nonexistent/path.json"})
        c.initialize()
        assert c.fetch("any") == {}

    def test_no_file_path_returns_empty(self):
        c = JSONFileConnector()
        c.initialize()
        assert c.fetch("any") == {}

    def test_test_connection_valid_file(self, json_file):
        c = JSONFileConnector(config={"file_path": json_file})
        c.initialize()
        assert c.test_connection() is True

    def test_test_connection_missing_file(self):
        c = JSONFileConnector(config={"file_path": "/no/such/file.json"})
        c.initialize()
        assert c.test_connection() is False

    def test_supports_source(self, json_file):
        c = JSONFileConnector(config={"file_path": json_file})
        c.initialize()
        assert c.supports_source("json") is True
        assert c.supports_source("file") is True
        assert c.supports_source("salesforce") is False

    def test_metadata(self, json_file):
        c = JSONFileConnector(config={"file_path": json_file})
        c.initialize()
        assert c.name == "json-file-connector"
        assert c.category == "data_connector"


# ── PluginManager find_ methods ───────────────────────────────────────────────


class TestPluginManagerNewFindMethods:
    @pytest.fixture
    def full_manager(self):
        m = PluginManager()
        m.registry.register_plugin(NoOpLLMAdapter, "llm_adapter", "noop-llm")
        m.registry.register_plugin(LiteLLMAdapter, "llm_adapter", "litellm")
        m.registry.register_plugin(
            JSONReportFormatter, "output_formatter", "json-report"
        )
        m.registry.register_plugin(
            PassthroughFormatter, "output_formatter", "passthrough-formatter"
        )
        m.registry.register_plugin(DictConnector, "data_connector", "dict-connector")
        m.registry.register_plugin(
            JSONFileConnector, "data_connector", "json-file-connector"
        )
        return m

    def test_find_llm_adapter_noop(self, full_manager):
        # LiteLLM (priority=100) beats NoOp (priority=1) and supports_model("noop") is True
        # So highest priority adapter that supports the model wins
        adapter = full_manager.find_llm_adapter("noop")
        assert adapter is not None
        # litellm has higher priority (100 vs 1) and supports any non-empty model string
        assert adapter.name in ("litellm", "noop-llm")

    def test_find_llm_adapter_any_model_returns_litellm(self, full_manager):
        # LiteLLM has priority=100, NoOp has priority=1
        # LiteLLM supports_model("gpt-4o") is True, NoOp is False
        adapter = full_manager.find_llm_adapter("gpt-4o")
        assert adapter is not None
        assert adapter.name == "litellm"

    def test_find_llm_adapter_no_match_returns_none(self):
        m = PluginManager()
        # No adapters registered
        assert m.find_llm_adapter("gpt-4o") is None

    def test_find_llm_adapter_no_model_returns_highest_priority(self, full_manager):
        # No model filter → highest priority wins → litellm (100) over noop (1)
        adapter = full_manager.find_llm_adapter("")
        assert adapter is not None
        assert adapter.name == "litellm"

    def test_find_output_formatter_json(self, full_manager):
        formatter = full_manager.find_output_formatter("json")
        assert formatter is not None
        assert formatter.name == "json-report"

    def test_find_output_formatter_passthrough(self, full_manager):
        formatter = full_manager.find_output_formatter("passthrough")
        assert formatter is not None
        assert formatter.name == "passthrough-formatter"

    def test_find_output_formatter_no_format_returns_highest_priority(
        self, full_manager
    ):
        # json-report (100) beats passthrough-formatter (1)
        formatter = full_manager.find_output_formatter("")
        assert formatter is not None
        assert formatter.name == "json-report"

    def test_find_output_formatter_no_match_returns_none(self):
        m = PluginManager()
        assert m.find_output_formatter("xml") is None

    def test_find_data_connector_dict(self, full_manager):
        connector = full_manager.find_data_connector("dict")
        assert connector is not None
        assert connector.name == "dict-connector"

    def test_find_data_connector_json(self, full_manager):
        connector = full_manager.find_data_connector("json")
        assert connector is not None
        # json-file-connector (50) beats dict-connector (1) for "json"
        assert connector.name == "json-file-connector"

    def test_find_data_connector_no_match_returns_none(self):
        m = PluginManager()
        assert m.find_data_connector("salesforce") is None

    def test_all_new_plugins_listed(self, full_manager):
        all_p = full_manager.list_plugins()
        assert "noop-llm" in all_p.get("llm_adapter", [])
        assert "litellm" in all_p.get("llm_adapter", [])
        assert "json-report" in all_p.get("output_formatter", [])
        assert "passthrough-formatter" in all_p.get("output_formatter", [])
        assert "dict-connector" in all_p.get("data_connector", [])
        assert "json-file-connector" in all_p.get("data_connector", [])


# ── Full pipeline: Sir's vision end-to-end ───────────────────────────────────


class TestSirVisionEndToEnd:
    """
    Tests the full pipeline Sir envisioned:
    DataConnector → LLMAdapter → (mapper) → OutputFormatter
    """

    def test_fetch_map_format_pipeline(self):
        """
        Simulate Sir's vision:
        1. DataConnector fetches investor data by record_id
        2. LLMAdapter maps PDF field names to schema keys
        3. OutputFormatter packages the result
        """
        # 1. Setup
        manager = PluginManager()
        manager.registry.register_plugin(
            DictConnector, "data_connector", "dict-connector"
        )
        manager.registry.register_plugin(NoOpLLMAdapter, "llm_adapter", "noop-llm")
        manager.registry.register_plugin(
            JSONReportFormatter, "output_formatter", "json-report"
        )

        # 2. Load investor data via connector
        data_store = {
            "investor_001": {
                "investor_name": "Jane Smith",
                "email_address": "jane@example.com",
                "commitment_usd": "500000",
            }
        }
        connector = DictConnector(config={"data": data_store})
        connector.initialize()
        investor_data = connector.fetch("investor_001")
        assert investor_data["investor_name"] == "Jane Smith"

        # 3. Map PDF field names using LLM adapter
        pdf_fields = ["investor_full_name", "email_addr", "commitment_amount"]
        schema_keys = list(investor_data.keys())

        adapter = manager.find_llm_adapter("noop")
        assert adapter is not None
        field_mapping = adapter.map_fields(pdf_fields, context="LP subscription form")
        assert isinstance(field_mapping, dict)
        assert len(field_mapping) == 3

        # 4. Embed schema metadata
        embedding = adapter.embed(pdf_fields, schema_keys)
        assert "investor_full_name" in embedding
        assert "schema_key" in embedding["investor_full_name"]

        # 5. Format the output
        filled_pdf_bytes = b"%PDF-1.4 ... filled content ..."
        formatter = manager.find_output_formatter("json")
        assert formatter is not None
        output = formatter.format(
            filled_pdf_bytes,
            investor_data,
            session_id="sess_abc",
            user_id="investor_001",
        )
        assert output["status"] == "ok"
        assert output["report"] == investor_data
        assert output["session_id"] == "sess_abc"
        assert "pdf_b64" in output

    def test_custom_llm_adapter_pattern_sir_readme(self):
        """
        Exactly Sir's README pattern:
            class MyCustomLLM(LLMAdapter):
                def map_fields(self, fields, context):
                    return {field: self.call_my_llm(field, context) for field in fields}
        """

        @plugin(category="llm_adapter", name="my-custom-llm")
        class MyCustomLLM(LLMAdapter):
            """Custom LLM that appends _mapped to each field name."""

            def get_metadata(self):
                return PluginMetadata(
                    name="my-custom-llm",
                    version="1.0.0",
                    author="Your Team",
                    description="My custom LLM",
                    category="llm_adapter",
                )

            def call_my_llm(self, field: str, context: str) -> str:
                # Simulate LLM returning canonical key
                return field.lower().replace(" ", "_") + "_key"

            def map_fields(self, fields, context):
                return {field: self.call_my_llm(field, context) for field in fields}

            def embed(self, fields, schema_keys):
                mapping = self.map_fields(fields, "")
                return {
                    f: {"schema_key": mapping[f], "confidence": 0.95} for f in fields
                }

        manager = PluginManager()
        manager.registry.register_plugin(MyCustomLLM, "llm_adapter", "my-custom-llm")

        llm = manager.load_plugin("my-custom-llm", "llm_adapter")
        assert llm is not None
        assert llm.name == "my-custom-llm"

        result = llm.map_fields(
            ["investor_full_name", "commitment_amount_usd"],
            "LP Subscription Agreement",
        )
        assert result["investor_full_name"] == "investor_full_name_key"
        assert result["commitment_amount_usd"] == "commitment_amount_usd_key"

    def test_salesforce_style_connector_pattern(self):
        """
        Sir's DataConnector pattern:
            class SalesforceConnector(DataConnectorPlugin):
                def fetch(self, record_id):
                    # Pull contact data from Salesforce
                    ...
        """

        @plugin(category="data_connector", name="salesforce-mock")
        class SalesforceConnector(DataConnectorPlugin):
            """Mock Salesforce connector for testing."""

            _MOCK_DB = {
                "003xx000004TmiQ": {
                    "investor_name": "Jane Smith",
                    "email": "jane@salesforce-example.com",
                    "account_type": "Individual",
                },
            }

            def get_metadata(self):
                return PluginMetadata(
                    name="salesforce-mock",
                    version="1.0.0",
                    author="Your Team",
                    description="Mock Salesforce connector",
                    category="data_connector",
                )

            def fetch(self, record_id: str, **kwargs) -> dict:
                # Pull contact data from Salesforce (mocked)
                return dict(self._MOCK_DB.get(record_id, {}))

        connector = SalesforceConnector()
        connector.initialize()

        data = connector.fetch("003xx000004TmiQ")
        assert data["investor_name"] == "Jane Smith"
        assert data["email"] == "jane@salesforce-example.com"

        # Missing record
        assert connector.fetch("nonexistent") == {}

    def test_json_report_formatter_sir_pattern(self):
        """
        Sir's OutputFormatter pattern:
            def format(self, filled_pdf: bytes, field_map: dict) -> dict:
                return {"pdf": filled_pdf, "report": field_map, "status": "ok"}
        """
        formatter = JSONReportFormatter()
        formatter.initialize()

        filled_pdf = b"%PDF-1.4 filled content"
        field_map = {"investor_name": "Jane Smith", "email": "jane@example.com"}

        result = formatter.format(filled_pdf, field_map)

        # Sir's exact expected keys
        assert "pdf_bytes" in result or "pdf_b64" in result
        assert result["report"] == field_map
        assert result["status"] == "ok"
