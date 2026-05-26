"""
Plugin benchmark tasks.

Each function returns a result dict with timing and metrics.
Called from run_benchmark.py.
"""

from __future__ import annotations

import os
import tempfile
import time
from typing import Any, Dict


def run_load_task(plugin_name: str = "email-validator") -> Dict[str, Any]:
    """Measure load + initialize time for a built-in plugin."""
    from pdf_autofillr_plugins import PluginManager
    from pdf_autofillr_plugins.builtin.validators.email_validator import (
        EmailValidatorPlugin,
    )

    start = time.perf_counter()
    manager = PluginManager()
    manager.registry.register_plugin(
        EmailValidatorPlugin, "validator", "email-validator"
    )
    manager.load_plugin("email-validator", "validator")
    manager.shutdown()
    return {
        "task": "load_plugin",
        "plugin": plugin_name,
        "duration_s": round(time.perf_counter() - start, 4),
    }


def run_validate_batch_task(n: int = 1000) -> Dict[str, Any]:
    """Measure validation throughput."""
    from pdf_autofillr_plugins import PluginManager
    from pdf_autofillr_plugins.builtin.validators.email_validator import (
        EmailValidatorPlugin,
    )

    manager = PluginManager()
    manager.registry.register_plugin(
        EmailValidatorPlugin, "validator", "email-validator"
    )
    validator = manager.load_plugin("email-validator", "validator")
    assert validator is not None

    emails = [f"user{i}@example.com" for i in range(n)]
    start = time.perf_counter()
    results = [validator.validate("email", e) for e in emails]  # type: ignore[union-attr, attr-defined]
    duration = time.perf_counter() - start

    manager.shutdown()
    return {
        "task": "validate_batch",
        "n": n,
        "duration_s": round(duration, 4),
        "per_item_ms": round(duration / n * 1000, 4),
        "items_per_sec": int(n / duration),
        "success_rate": sum(1 for r in results if r["valid"]) / n,
    }


def run_mapping_task(n_fields: int = 5) -> Dict[str, Any]:
    """Measure identity mapper coverage."""
    from pdf_autofillr_plugins import PluginManager
    from pdf_autofillr_plugins.builtin.mappers.identity_mapper import (
        IdentityMapperPlugin,
    )

    fields = [
        {"name": f"field_{i}", "value": f"value_{i}", "confidence": 0.9}
        for i in range(n_fields)
    ]
    schema = {f"field_{i}": "string" for i in range(n_fields)}

    manager = PluginManager()
    manager.registry.register_plugin(IdentityMapperPlugin, "mapper", "identity-mapper")
    mapper = manager.load_plugin("identity-mapper", "mapper")
    assert mapper is not None

    start = time.perf_counter()
    result = mapper.map_fields(fields, schema)  # type: ignore[union-attr, attr-defined]
    duration_ms = (time.perf_counter() - start) * 1000

    manager.shutdown()
    return {
        "task": "mapping",
        "n_fields": n_fields,
        "coverage": result["coverage"],
        "duration_ms": round(duration_ms, 4),
    }


def run_discovery_task(n_plugins: int = 3) -> Dict[str, Any]:
    """Measure discovery time from a temp directory with multiple plugins."""
    from pdf_autofillr_plugins import PluginManager

    plugin_template = """
from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces.validator_plugin import ValidatorPlugin
from pdf_autofillr_plugins.interfaces.base_plugin import PluginMetadata

@plugin(category="validator", name="bench-plugin-{i}")
class BenchPlugin{i}(ValidatorPlugin):
    def get_metadata(self):
        return PluginMetadata(name="bench-plugin-{i}", version="1.0", author="Bench",
                              description="", category="validator")
    def validate(self, name, value, rules=None, **kw):
        return {{"valid": True, "errors": [], "warnings": [], "validator": "bench-plugin-{i}"}}
    def supports_field_type(self, ft): return True
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(n_plugins):
            with open(os.path.join(tmpdir, f"bench_plugin_{i}.py"), "w") as f:
                f.write(plugin_template.format(i=i))

        start = time.perf_counter()
        manager = PluginManager()
        discovered = manager.discover_plugins([tmpdir])
        duration_ms = (time.perf_counter() - start) * 1000

    return {
        "task": "discovery",
        "n_plugins_written": n_plugins,
        "n_plugins_found": sum(len(v) for v in discovered.values()),
        "duration_ms": round(duration_ms, 2),
    }
