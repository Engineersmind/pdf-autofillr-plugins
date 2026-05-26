"""
DataConnectorPlugin — Plugin interface for external data connectors.

Pull fill data from CRMs, databases, APIs, or any external source
at fill time — instead of passing data in manually.

Sir's original vision::

    class SalesforceConnector(DataConnectorPlugin):
        name = "salesforce"

        def fetch(self, record_id: str) -> dict:
            # Pull contact data from Salesforce
            ...
"""
from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List

from pdf_autofillr_plugins.interfaces.base_plugin import BasePlugin, PluginMetadata


class DataConnectorPlugin(BasePlugin):
    """
    Base class for data connector plugins.

    Data connectors pull field values from external sources (CRMs,
    databases, REST APIs, spreadsheets, etc.) at fill time. Instead
    of passing a data dict manually, the pipeline calls fetch() and
    uses the returned values to fill the PDF.

    Minimum implementation::

        from pdf_autofillr_plugins import plugin
        from pdf_autofillr_plugins.interfaces import DataConnectorPlugin, PluginMetadata

        @plugin(category="data_connector", name="salesforce")
        class SalesforceConnector(DataConnectorPlugin):

            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="salesforce", version="1.0.0",
                    author="Your Team", description="Pulls investor data from Salesforce",
                    category="data_connector",
                )

            def fetch(self, record_id: str) -> dict:
                # Call Salesforce API and return a flat field dict
                return {
                    "investor_name": "Jane Smith",
                    "email": "jane@example.com",
                    "commitment_usd": "500000",
                }
    """

    @abstractmethod
    def fetch(self, record_id: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch field data for a given record from the external source.

        Args:
            record_id: Unique identifier for the record to fetch
                       (CRM contact ID, database row ID, API resource ID, etc.)
            **kwargs:  Additional source-specific parameters
                       (table name, query filters, field selection, etc.)

        Returns:
            Flat dict of field_name → value, ready to pass to the mapper::

                {
                    "investor_name": "Jane Smith",
                    "email":         "jane@example.com",
                    "commitment_usd": "500000",
                }
        """
        pass

    def fetch_batch(
        self,
        record_ids: List[str],
        **kwargs,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch data for multiple records at once.

        Default implementation calls fetch() for each ID sequentially.
        Override for batch API support.

        Args:
            record_ids: List of record identifiers
            **kwargs:   Passed through to fetch()

        Returns:
            Dict of record_id → field data dict
        """
        return {rid: self.fetch(rid, **kwargs) for rid in record_ids}

    def supports_source(self, source_name: str) -> bool:
        """
        Check if this connector supports a named data source.

        Args:
            source_name: e.g. "salesforce", "hubspot", "postgres"

        Returns:
            True if supported
        """
        return False

    def get_supported_sources(self) -> List[str]:
        """
        List data sources this connector can pull from.

        Returns:
            List of source name strings
        """
        return []

    def test_connection(self) -> bool:
        """
        Test that the external data source is reachable.

        Override to add a real connectivity check.

        Returns:
            True if connection is healthy
        """
        return True

    def get_metadata(self) -> PluginMetadata:
        """Default metadata — override with your own."""
        return PluginMetadata(
            name=self.__class__.__name__,
            version="1.0.0",
            author="Unknown",
            description="Custom data connector",
            category="data_connector",
        )
