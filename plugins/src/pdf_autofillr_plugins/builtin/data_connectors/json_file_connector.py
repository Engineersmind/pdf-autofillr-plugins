"""
Built-in: JSONFileConnector

Loads fill data from a JSON file on disk, keyed by record_id.
The file format is {record_id: {field_name: value}}.

Registered under category="data_connector", name="json-file-connector".

Config:
    file_path (str): Path to the JSON file (required)

Example JSON file::

    {
        "user_001": {"investor_name": "Jane Smith", "email": "jane@example.com"},
        "user_002": {"investor_name": "John Doe",  "email": "john@example.com"}
    }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import PluginMetadata
from pdf_autofillr_plugins.interfaces.data_connector import DataConnectorPlugin


@plugin(
    category="data_connector",
    name="json-file-connector",
    version="1.0.0",
    author="Engineers Mind",
    description="JSON file connector — loads fill data from a .json file keyed by record_id",
    tags=["json", "file", "builtin"],
    priority=50,
)
class JSONFileConnector(DataConnectorPlugin):
    """
    JSON file data connector.

    Loads a JSON file on initialize() and serves field data by record_id.

    Config:
        file_path (str): Path to the JSON data file
    """

    def initialize(self) -> None:
        file_path = self.get_config_value("file_path", None)
        self._data: Dict[str, Dict[str, Any]] = {}
        if file_path and Path(file_path).exists():
            with open(file_path, encoding="utf-8") as f:
                self._data = json.load(f)
        super().initialize()

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="json-file-connector",
            version="1.0.0",
            author="Engineers Mind",
            description="JSON file connector — loads fill data from a .json file keyed by record_id",
            category="data_connector",
            tags=["json", "file", "builtin"],
        )

    def fetch(self, record_id: str, **kwargs) -> Dict[str, Any]:
        return dict(self._data.get(record_id, {}))

    def supports_source(self, source_name: str) -> bool:
        return source_name.lower() in {"json", "file", "json-file"}

    def get_supported_sources(self) -> List[str]:
        return ["json", "file", "json-file"]

    def test_connection(self) -> bool:
        file_path = self.get_config_value("file_path", None)
        return file_path is not None and Path(file_path).exists()
