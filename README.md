# Python Serialization Benchmark

This project measures maintained Python serialization libraries at equivalent abstraction levels. Every selected adapter must pass exact semantic validation before it can be timed.

## What is compared

The primitive tier measures conversion between canonical stdlib dataclass instances and JSON-compatible Python values. It includes:

- Handwritten conversion
- `dataclasses.asdict` (dump only)
- Marshmallow
- Django REST Framework
- cattrs
- mashumaro
- msgspec
- Pydantic v2
- serpyco-rs
- Adaptix 3.0 beta (prerelease)

The encoded tier measures conversion between the same model and bytes, partitioned by format. It includes:

- JSON: stdlib `json`, orjson, msgspec, mashumaro, Pydantic, and serpyco-rs
- MessagePack: msgspec, mashumaro, serpyco-rs, and ormsgpack
- Avro: the maintained `avro` distribution
- Python object persistence: stdlib `pickle`

## What is not compared

Results from different encoded formats are not comparable. Format-crossing rankings, such as JSON against MessagePack, are invalid. Composite scores across formats or operations are also invalid and are deliberately not produced.

## Methodology

All adapters use the same canonical stdlib dataclasses and deterministic fixtures. The single-object cases and 100-object batch cases are measured separately. Adapter construction, schema setup, code generation, converters, and prepared decode inputs live outside the timed operation.

Correctness is a gate, not an assumption. Before timing an adapter, the runner validates exact primitive output or normalized round trips, batch order and cardinality, encoded return types, and deterministic payload lengths. Garbage collection remains enabled and is recorded in the raw metadata. `pyperf` controls processes, warmups, loop calibration, and environment metadata. Encoded reports include payload sizes alongside timing data.

## Canonical results

The versioned 2026-09-06 snapshot is available as separate [primitive](results/reports/2026-09-06-cpython-3.14-primitive.md) and [encoded](results/reports/2026-09-06-cpython-3.14-encoded.md) reports. These are machine-specific measurements, not a portable performance baseline.

The snapshot used CPython 3.14.6 (64-bit) on macOS 15.5, arm64, with an Apple M2 CPU (8 cores: 4 performance and 4 efficiency). Garbage collection was enabled. The primitive suite ran at `2026-09-06T23:52:07.196571+00:00` from revision `c1f0a332e358bd358330471aab22edad48e7b5d6`; the encoded suite ran at `2026-09-07T01:23:12.085278+00:00` from revision `10de3a659951cd6ce359a41b47c93db48ec675d1`.

## Install and validate

Python 3.12, 3.13, and 3.14 are supported. Python 3.14 is the canonical benchmark runtime.

```bash
uv sync --locked
uv run pytest
uv run serialization-benchmark validate
```

## Run benchmarks

Use the smoke commands to verify the benchmark wiring quickly:

```bash
uv run serialization-benchmark run primitive --output results/raw/primitive-smoke.json --adapter handwritten --operation dump_one -- --processes=1 --values=1 --warmups=1 --loops=1
uv run serialization-benchmark run encoded --output results/raw/encoded-smoke.json --adapter msgspec-json --operation encode_one -- --processes=1 --values=1 --warmups=1 --loops=1
```

Use rigorous runs for complete measurements. These take substantially longer:

```bash
uv run serialization-benchmark run primitive --output results/raw/primitive.json -- --rigorous
uv run serialization-benchmark run encoded --output results/raw/encoded.json -- --rigorous
```

## Generate reports

Generate each format-partitioned Markdown and HTML report from its raw `pyperf` data:

```bash
uv run serialization-benchmark report results/raw/primitive.json --markdown results/reports/primitive.md --html results/reports/primitive.html
uv run serialization-benchmark report results/raw/encoded.json --markdown results/reports/encoded.md --html results/reports/encoded.html
```

## Docker

The Compose services reproduce the locked Python 3.14 environment. The primitive and encoded services write smoke results into the host `results/raw` directory.

```bash
docker compose build
docker compose run --rm validate
docker compose run --rm tests
docker compose run --rm primitive
docker compose run --rm encoded
```

## Interpreting results

Compare rows only within the same tier, format, operation, batch size, and model strategy. Relative values are meaningful only against the baseline in that table. Measurements from different machines are not directly comparable, including results from different hosted CI runners.

## Pickle safety

Never decode pickle bytes from an untrusted source. Pickle can execute arbitrary code while loading data and is included only as a Python object-persistence benchmark.

## Adding an adapter

Implement the appropriate primitive or encoded adapter contract, add an explicit instance to `serialization_benchmark.registry`, and declare its stable metadata and supported operations. The adapter must pass exact contract validation for every registered operation. Encoded adapters must declare their format so reports keep results in the correct format partition.
