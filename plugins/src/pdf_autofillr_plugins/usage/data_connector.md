# DataConnectorPlugin — Usage Guide

Pull fill data from CRMs, databases, APIs, or any external source at fill time.

## Write the plugin

```python
# my_plugins/salesforce_connector.py
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import DataConnectorPlugin, PluginMetadata

@plugin(
    category="data_connector",
    name="salesforce",
    version="1.0.0",
    author="Your Team",
    description="Pulls investor data from Salesforce",
)
class SalesforceConnector(DataConnectorPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="salesforce", version="1.0.0",
            author="Your Team", description="Salesforce data connector",
            category="data_connector",
        )

    def initialize(self):
        # Set up Salesforce client
        self.api_key = self.get_config_value("api_key", "")
        super().initialize()

    def fetch(self, record_id: str, **kwargs) -> dict:
        # Pull contact data from Salesforce
        # response = salesforce_client.get_contact(record_id)
        return {
            "investor_name": "Jane Smith",
            "email": "jane@example.com",
            "commitment_usd": "500000",
        }
```

## Use the built-in dict connector (testing)

```python
from pdf_autofillr_plugins.builtin.data_connectors.dict_connector import DictConnector

connector = DictConnector(config={
    "data": {
        "user_001": {"investor_name": "Jane Smith", "email": "jane@example.com"},
        "user_002": {"investor_name": "John Doe",  "email": "john@example.com"},
    }
})
connector.initialize()

data = connector.fetch("user_001")
# {"investor_name": "Jane Smith", "email": "jane@example.com"}

batch = connector.fetch_batch(["user_001", "user_002"])
# {"user_001": {...}, "user_002": {...}}
```

## Use the built-in JSON file connector

```python
from pdf_autofillr_plugins.builtin.data_connectors.json_file_connector import JSONFileConnector

# investors.json: {"user_001": {"investor_name": "Jane", ...}}
connector = JSONFileConnector(config={"file_path": "data/investors.json"})
connector.initialize()

data = connector.fetch("user_001")
```

## Expected output

```python
{
    "investor_name": "Jane Smith",
    "email": "jane@example.com",
    "commitment_usd": "500000",
}
```
