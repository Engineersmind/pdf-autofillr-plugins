"""Plugin benchmark tasks — measure plugin load time, execution, and throughput."""
import time
from pdf_autofillr_plugins import PluginManager
from pdf_autofillr_plugins.builtin.validators.email_validator import EmailValidatorPlugin

def run_load_task():
    start = time.time()
    manager = PluginManager()
    manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
    manager.load_plugin("email-validator", "validator")
    manager.shutdown()
    return {"task": "load_email_validator", "duration_s": round(time.time()-start, 4)}

def run_validate_batch_task(n=1000):
    manager = PluginManager()
    manager.registry.register_plugin(EmailValidatorPlugin, "validator", "email-validator")
    v = manager.load_plugin("email-validator", "validator")
    emails = [f"user{i}@example.com" for i in range(n)]
    start = time.time()
    results = [v.validate("email", e) for e in emails]
    duration = time.time() - start
    return {
        "task": "validate_batch",
        "n": n,
        "duration_s": round(duration, 4),
        "per_item_ms": round(duration/n*1000, 4),
        "success_rate": sum(1 for r in results if r["valid"]) / n,
    }
