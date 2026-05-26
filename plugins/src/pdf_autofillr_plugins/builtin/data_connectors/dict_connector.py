"""
Built-in: DictConnector

Serves fill data from an in-memory dict keyed by record_id.
Used for testing and simple pipelines where data is already in memory.

Registered under category="data_connector", name="dict-connector".

This is analogous to what Sir envisioned — a connector that
fetches data for a record_id from an external source. Here
the "source" is a pre-loaded in-memory dict.

Config:
    data (dict): {record_id: {field: value}} mapping
"""
from __future__ import annotations

from typing import Any, Dict, List

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import PluginMetadata
from pdf_autofillr_plugins.interfaces.data_connector import DataConnectorPlugin


@plugin(
    category="data_connector",
    name="dict-connector",
    version="1.0.0",
    author="Engineers Mind",
    description="In-memory dict connector — serves field data by record_id. Use for testing.",
    tags=["dict", "in-memory", "testing", "builtin"],
    priority=1,
)
class DictConnector(DataConnectorPlugin):
    """
    In-memory dict data connector.

    Serves pre-loaded field data by record_id. Useful for:
    - Unit testing without external dependencies
    - Simple pipelines where data is already in memory
    - Prototyping before wiring a real CRM connector

    Config:
        data (dict): {record_id: {field_name: value}} — the data store

    Usage::

        connector = DictConnector(config={
            "data": {
                "user_001": {"investor_name": "Jane Smith", "email": "jane@example.com"},
                "user_002": {"investor_name": "John Doe",  "email": "john@example.com"},
            }
        })
        connector.initialize()

        data = connector.fetch("user_001")
        # {"investor_name": "Jane Smith", "email": "jane@example.com"}
    """

    def initialize(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = self.get_config_value("data", {})
        super().initialize()

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dict-connector",
            version="1.0.0",
            author="Engineers Mind",
            description="In-memory dict connector — serves field data by record_id",
            category="data_connector",
            tags=["dict", "in-memory", "testing", "builtin"],
        )

    def fetch(self, record_id: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch field data for a record_id from the in-memory store.

        Args:
            record_id: Key into the data dict

        Returns:
            Field data dict, or empty dict if record not found
        """
        return dict(self._data.get(record_id, {}))

    def fetch_batch(self, record_ids: List[str], **kwargs) -> Dict[str, Dict[str, Any]]:
        return {rid: self.fetch(rid) for rid in record_ids}

    def supports_source(self, source_name: str) -> bool:
        return source_name.lower() in {"dict", "memory", "in-memory"}

    def get_supported_sources(self) -> List[str]:
        return ["dict", "memory", "in-memory"]

    def test_connection(self) -> bool:
        return isinstance(self._data, dict)
