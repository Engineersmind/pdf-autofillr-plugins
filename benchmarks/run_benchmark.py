"""
pdf-autofillr-plugins benchmark runner.
"""
import json, time
from pathlib import Path

RESULTS_DIR = Path("benchmarks/results")

def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    results = []

    print("\npdf-autofillr-plugins benchmark")
    print("─" * 40)

    # Load benchmark
    from pdf_autofillr_plugins import PluginManager
    from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

    start = time.time()
    manager = PluginManager()
    manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
    v = manager.load_plugin("email-validator", "validator")
    load_time = time.time() - start
    print(f"  ✅  load email-validator      {load_time*1000:.2f}ms")
    results.append({"task": "load", "duration_ms": round(load_time*1000, 2)})

    # Throughput benchmark
    n = 1000
    emails = [f"user{i}@example.com" for i in range(n)]
    start = time.time()
    for e in emails:
        v.validate("email", e)
    duration = time.time() - start
    per_item_ms = duration / n * 1000
    print(f"  ✅  validate {n} emails        {per_item_ms:.3f}ms/item  ({int(1000/per_item_ms)} items/sec)")
    results.append({"task": "validate_batch", "n": n, "per_item_ms": round(per_item_ms, 3)})

    manager.shutdown()

    out = RESULTS_DIR / "benchmark_results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out}\n")

if __name__ == "__main__":
    main()
