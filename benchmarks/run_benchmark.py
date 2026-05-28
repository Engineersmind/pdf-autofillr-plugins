"""
pdf-autofillr-plugins — benchmark runner.

Measures plugin load time, validation throughput, mapping coverage,
and plugin discovery time.

Usage:
    python benchmarks/run_benchmark.py

Results are written to benchmarks/results/benchmark_results.json.
"""

from __future__ import annotations

import json
import time
import tempfile
import os
from pathlib import Path

RESULTS_DIR = Path("benchmarks/results")


def _separator(label: str) -> None:
    print(f"\n  {label}")
    print("  " + "─" * 50)


def bench_plugin_load() -> dict:
    """Measure time to load and initialize EmailValidatorPlugin."""
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
    duration_ms = (time.perf_counter() - start) * 1000
    manager.shutdown()

    print(f"  ✅  load email-validator          {duration_ms:.2f}ms")
    return {
        "task": "load_plugin",
        "plugin": "email-validator",
        "duration_ms": round(duration_ms, 2),
    }


def bench_validate_throughput(n: int = 1000) -> dict:
    """Measure validation throughput (items/sec)."""
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

    per_item_ms = duration / n * 1000
    items_per_sec = int(1000 / per_item_ms)
    success_rate = sum(1 for r in results if r["valid"]) / n

    manager.shutdown()
    print(
        f"  ✅  validate {n} emails             {per_item_ms:.3f}ms/item  ({items_per_sec:,} items/sec)  {success_rate:.0%} valid"
    )
    return {
        "task": "validate_throughput",
        "n": n,
        "per_item_ms": round(per_item_ms, 3),
        "items_per_sec": items_per_sec,
        "success_rate": success_rate,
    }


def bench_mapping_coverage() -> dict:
    """Measure IdentityMapperPlugin coverage on a sample field set."""
    from pdf_autofillr_plugins import PluginManager
    from pdf_autofillr_plugins.builtin.mappers.identity_mapper import (
        IdentityMapperPlugin,
    )

    manager = PluginManager()
    manager.registry.register_plugin(IdentityMapperPlugin, "mapper", "identity-mapper")
    mapper = manager.load_plugin("identity-mapper", "mapper")
    assert mapper is not None

    fields = [
        {"name": "investor_name", "value": "Jane Smith", "confidence": 0.99},
        {"name": "email_address", "value": "jane@example.com", "confidence": 0.98},
        {"name": "commitment_usd", "value": "500000", "confidence": 0.95},
        {"name": "unknown_field", "value": "???", "confidence": 0.5},
    ]
    schema = {
        "investor_name": "string",
        "email_address": "string",
        "commitment_usd": "string",
    }

    start = time.perf_counter()
    result = mapper.map_fields(fields, schema)  # type: ignore[union-attr, attr-defined]
    duration_ms = (time.perf_counter() - start) * 1000

    manager.shutdown()
    coverage = result["coverage"]
    print(f"  ✅  identity-mapper coverage       {coverage:.0%}  ({duration_ms:.2f}ms)")
    return {
        "task": "mapping_coverage",
        "coverage": coverage,
        "duration_ms": round(duration_ms, 2),
        "mapped": len(result["mapped_fields"]),
        "unmapped": len(result["unmapped_fields"]),
    }


def bench_ml_mapper_throughput(n: int = 500) -> dict:
    """Measure MLMapperPlugin synonym lookup throughput."""
    from pdf_autofillr_plugins import PluginManager
    from pdf_autofillr_plugins.builtin.mappers.ml_mapper import MLMapperPlugin

    manager = PluginManager()
    manager.registry.register_plugin(MLMapperPlugin, "mapper", "ml-mapper")
    mapper = manager.load_plugin("ml-mapper", "mapper")
    assert mapper is not None

    # Use fields that hit synonym table
    fields_batch = [
        {"name": "first_name", "value": "Jane", "confidence": 0.9},
        {"name": "email", "value": "jane@corp.com", "confidence": 0.9},
        {"name": "invoice_number", "value": "INV-001", "confidence": 0.9},
    ]

    start = time.perf_counter()
    for _ in range(n):
        mapper.map_fields(fields_batch)  # type: ignore[union-attr, attr-defined]
    duration = time.perf_counter() - start

    per_call_ms = duration / n * 1000
    manager.shutdown()
    print(
        f"  ✅  ml-mapper {n} calls             {per_call_ms:.3f}ms/call  ({int(1000/per_call_ms):,} calls/sec)"
    )
    return {
        "task": "ml_mapper_throughput",
        "n": n,
        "per_call_ms": round(per_call_ms, 3),
        "calls_per_sec": int(1000 / per_call_ms),
    }


def bench_discovery_time() -> dict:
    """Measure plugin discovery time from a temp directory."""
    from pdf_autofillr_plugins import PluginManager

    plugin_code = """
from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces.validator_plugin import ValidatorPlugin
from pdf_autofillr_plugins.interfaces.base_plugin import PluginMetadata

@plugin(category="validator", name="bench-plugin")
class BenchPlugin(ValidatorPlugin):
    def get_metadata(self):
        return PluginMetadata(name="bench-plugin", version="1.0", author="Bench",
                              description="", category="validator")
    def validate(self, name, value, rules=None, **kw):
        return {"valid": True, "errors": [], "warnings": [], "validator": "bench-plugin"}
    def supports_field_type(self, ft): return True
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "bench_plugin.py"), "w") as f:
            f.write(plugin_code)

        start = time.perf_counter()
        manager = PluginManager()
        discovered = manager.discover_plugins([tmpdir])
        duration_ms = (time.perf_counter() - start) * 1000

        n_discovered = sum(len(v) for v in discovered.values())
        print(
            f"  ✅  discovery from dir           {duration_ms:.2f}ms  ({n_discovered} plugin(s) found)"
        )
        return {
            "task": "discovery_time",
            "duration_ms": round(duration_ms, 2),
            "plugins_found": n_discovered,
        }


def main() -> None:
    print("\n  pdf-autofillr-plugins benchmark")
    print("  " + "═" * 50)

    results = []

    _separator("Plugin load")
    results.append(bench_plugin_load())

    _separator("Validation throughput")
    results.append(bench_validate_throughput(n=1000))

    _separator("Mapping coverage")
    results.append(bench_mapping_coverage())

    _separator("ML mapper throughput")
    results.append(bench_ml_mapper_throughput(n=500))

    _separator("Plugin discovery")
    results.append(bench_discovery_time())

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "benchmark_results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\n  Results saved → {out}\n")


if __name__ == "__main__":
    main()
