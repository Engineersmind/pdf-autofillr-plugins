"""
Plugin benchmark metric calculations.

Aggregates results from plugin_tasks.py into summary statistics.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def calculate_throughput(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Aggregate throughput from validate_batch results."""
    batch = [r for r in results if r.get("task") == "validate_batch"]
    if not batch:
        return {}
    avg_per_item = sum(r["per_item_ms"] for r in batch) / len(batch)
    return {
        "avg_per_item_ms": round(avg_per_item, 4),
        "items_per_sec": round(1000 / avg_per_item, 1),
        "samples": len(batch),
    }


def calculate_load_stats(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Aggregate plugin load time statistics."""
    loads = [r for r in results if r.get("task") == "load_plugin"]
    if not loads:
        return {}
    durations = [r["duration_ms"] for r in loads if "duration_ms" in r]
    if not durations:
        durations = [r["duration_s"] * 1000 for r in loads if "duration_s" in r]
    return {
        "min_ms": round(min(durations), 2),
        "max_ms": round(max(durations), 2),
        "avg_ms": round(sum(durations) / len(durations), 2),
        "samples": len(durations),
    }


def calculate_coverage_stats(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Aggregate mapping coverage from mapping results."""
    mappings = [r for r in results if r.get("task") in ("mapping", "mapping_coverage")]
    if not mappings:
        return {}
    coverages = [r["coverage"] for r in mappings if "coverage" in r]
    return {
        "avg_coverage": round(sum(coverages) / len(coverages), 4),
        "min_coverage": round(min(coverages), 4),
        "max_coverage": round(max(coverages), 4),
        "samples": len(coverages),
    }


def calculate_discovery_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate discovery timing."""
    discoveries = [r for r in results if r.get("task") in ("discovery", "discovery_time")]
    if not discoveries:
        return {}
    durations = [r["duration_ms"] for r in discoveries if "duration_ms" in r]
    return {
        "avg_discovery_ms": round(sum(durations) / len(durations), 2),
        "samples": len(durations),
    }


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Full benchmark summary."""
    return {
        "throughput": calculate_throughput(results),
        "load": calculate_load_stats(results),
        "coverage": calculate_coverage_stats(results),
        "discovery": calculate_discovery_stats(results),
        "total_tasks": len(results),
    }
