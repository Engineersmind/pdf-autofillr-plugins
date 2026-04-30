"""Plugin benchmark metric calculations."""
from typing import List, Dict, Any

def calculate_throughput(results: List[Dict[str, Any]]) -> Dict[str, float]:
    batch_results = [r for r in results if r.get("task") == "validate_batch"]
    if not batch_results: return {}
    avg_per_item = sum(r["per_item_ms"] for r in batch_results) / len(batch_results)
    return {"avg_per_item_ms": round(avg_per_item, 4), "items_per_sec": round(1000/avg_per_item, 1)}
