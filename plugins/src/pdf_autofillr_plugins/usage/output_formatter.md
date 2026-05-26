# OutputFormatterPlugin — Usage Guide

Control how filled PDFs and metadata are packaged and returned.

## Write the plugin

```python
# my_plugins/my_formatter.py
from pdf_autofillr_plugins import plugin
from pdf_autofillr_plugins.interfaces import OutputFormatterPlugin, PluginMetadata

@plugin(
    category="output_formatter",
    name="json-report",
    version="1.0.0",
    author="Your Team",
    description="Wraps filled PDF in JSON report",
)
class MyJSONFormatter(OutputFormatterPlugin):

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="json-report", version="1.0.0",
            author="Your Team", description="JSON report formatter",
            category="output_formatter",
        )

    def format(self, filled_pdf: bytes, field_map: dict, **kwargs) -> dict:
        return {
            "pdf": filled_pdf,
            "report": field_map,
            "status": "ok",
            "field_count": len(field_map),
        }
```

## Use the built-in JSON report formatter

```python
from pdf_autofillr_plugins.builtin.output_formatters.json_report_formatter import JSONReportFormatter

formatter = JSONReportFormatter()
formatter.initialize()

result = formatter.format(
    filled_pdf=b"%PDF filled bytes",
    field_map={"investor_name": "Jane Smith", "email": "jane@example.com"},
    session_id="sess_001",
    user_id="user_abc",
)
# {
#   "status": "ok",
#   "field_count": 2,
#   "report": {"investor_name": "Jane Smith", "email": "jane@example.com"},
#   "pdf_b64": "...",
#   "timestamp": "2026-05-24T12:00:00Z",
#   "session_id": "sess_001",
# }
```

## Expected output keys

- `status` — "ok" or "partial"
- `field_count` — number of filled fields
- `report` — the field_map dict
- `pdf_b64` — base64-encoded PDF (JSON-safe)
- `pdf_bytes` — raw PDF bytes (for in-process use)
- `timestamp` — ISO 8601 fill time
- `session_id`, `user_id`, `pdf_path` — if provided as kwargs
