# Python Serialization Benchmark

This project compares Python model serialization at equivalent abstraction levels. Every adapter must pass exact semantic validation before it can be timed. The active adapter registry is the source of truth; abandoned implementations are not retained.

The initial cutover provides handwritten model-to-primitive conversion and `dataclasses.asdict`. The latter is intentionally dump-only.

## Validate

```bash
uv sync --locked
uv run pytest
uv run serialization-benchmark validate
```

Python 3.12, 3.13, and 3.14 are supported. Python 3.14 is the canonical benchmark runtime.
