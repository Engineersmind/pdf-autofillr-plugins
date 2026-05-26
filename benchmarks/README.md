# pdf-autofillr-plugins — Benchmarks

Performance benchmarks for plugin loading, discovery, execution, and throughput.
Six document domains are included as dataset placeholders.

## Running

```bash
# From repo root
make benchmark

# Or directly
pip install -e "plugins/.[dev]"
python benchmarks/run_benchmark.py
```

Results are written to `benchmarks/results/benchmark_results.json`.

## What is measured

| Metric | Description |
|--------|-------------|
| **Plugin load time** | Time to instantiate and initialize a plugin |
| **Validation throughput** | Items/sec for `EmailValidatorPlugin.validate()` |
| **Mapping coverage** | Fraction of fields mapped by `IdentityMapperPlugin` |
| **Discovery time** | Time to scan a directory for plugin classes |

## Dataset domains

Each domain in `benchmarks/datasets/` has three subdirectories:

- `pdfs/` — placeholder for blank PDF forms
- `schema_keys/` — placeholder for `form_keys.json` field schemas
- `ground_truth/` — placeholder for expected extraction/mapping output

| Domain | Typical use case |
|--------|-----------------|
| `financial` | LP subscription agreements, investment forms |
| `government` | Tax forms, permit applications |
| `hr` | Employee onboarding, benefits enrollment |
| `insurance` | Claims forms, policy applications |
| `legal` | Contracts, NDAs, agreement forms |
| `medical` | Patient intake, consent forms |

## Model configs

`benchmarks/models/` contains YAML configs for LLM benchmark runs.
These are used when benchmarking mapper plugins that use LLM calls.

```yaml
# Example: benchmarks/models/gpt-4o-mini.yaml
model: openai/gpt-4o-mini
max_tokens: 1000
temperature: 0
```

## Adding a new benchmark task

1. Add your task function to `benchmarks/tasks/plugin_tasks.py`
2. Call it from `benchmarks/run_benchmark.py`
3. Add metric calculations to `benchmarks/metrics/plugin_metrics.py`
