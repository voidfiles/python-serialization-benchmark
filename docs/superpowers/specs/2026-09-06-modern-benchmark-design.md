# Modern Serialization Benchmark Design

## Purpose

Modernize `python-serialization-benchmark` into a reproducible comparison of maintained Python serialization libraries. The new benchmark must distinguish model conversion from wire encoding, validate semantic correctness before measuring speed, and publish raw measurements with enough metadata to reproduce them.

This is a replacement for the current benchmark architecture. Abandoned libraries and their compatibility machinery will be deleted rather than kept in a legacy environment. Git history is the historical archive.

## Goals

- Compare maintained serializers at equivalent abstraction levels.
- Measure serialization and deserialization separately for one object and a batch of 100 objects.
- Validate every adapter against one canonical semantic fixture before timing it.
- Record raw `pyperf` data, environment metadata, summarized results, and encoded payload sizes.
- Provide a locked `uv` environment that supports Python 3.12, 3.13, and 3.14.
- Keep the adapter API small enough that adding a library does not require changing the runner or report generator.

## Non-goals

- Preserving abandoned serializers as runnable code.
- Producing a single overall score across operations or formats.
- Treating hosted CI timing as a stable regression gate.
- Measuring schema construction, code generation, or import time in the primary throughput suite.
- Adding the P1 candidates before the P0 contracts and reports are stable.

## Active Scope

### Primitive tier

The primitive tier measures conversion between a model and JSON-compatible Python values. Its initial subjects are:

- handwritten conversion
- `dataclasses.asdict` as a dump-only baseline
- Marshmallow
- Django REST Framework
- msgspec
- mashumaro
- cattrs
- Pydantic v2
- serpyco-rs
- Adaptix 3.0 beta, explicitly labeled as a prerelease

Each result belongs to exactly one operation: `dump_one`, `load_one`, `dump_many`, or `load_many`. Unsupported operations are omitted and reported as unsupported, never synthesized from an unrelated API.

### Encoded tier

The encoded tier measures conversion between the same semantic fixture and bytes. Results are partitioned by format:

- JSON: stdlib `json` plus handwritten conversion, orjson, msgspec, mashumaro, Pydantic, and serpyco-rs
- MessagePack: msgspec, mashumaro, serpyco-rs, and ormsgpack
- Avro: the maintained `avro` distribution
- Python object persistence: pickle

Each encoded result belongs to one format and one operation, `encode_one`, `decode_one`, `encode_many`, or `decode_many`. The report must not rank different formats against each other. It records encoded byte length beside timing results.

## Removed Scope

Delete the implementations and direct dependencies for Serpy, the old Python serpyco package, Strainer, Lollipop, Kim, Toasted Marshmallow, Colander, and Lima. Remove the `collections` compatibility monkeypatches along with the libraries that require them. Remove historical entries from active documentation and reports instead of carrying static legacy tables forward.

The current `subjects` package is replaced completely. Avro and pickle move to encoded adapters; current Marshmallow and Django REST Framework integrations are rewritten against the new contracts.

## Canonical Data Model

The benchmark owns ordinary, mutable stdlib dataclasses named `Child` and `Parent`. They avoid inheritance, slots, frozen instances, aliases, and computed properties so every subject receives the same uncomplicated semantic workload. `Parent` contains scalar fields, one nested child, and a list of children.

A deterministic fixture factory creates:

- one canonical parent for single-object cases
- 100 semantically distinct parents for batch cases
- the exact JSON-compatible dictionary equivalents used by load and decode cases

The fixture values vary by index so a batch is not 100 references to the same object. Dumped primitives must exactly equal the canonical dictionaries. Loaded or decoded values are normalized to `Parent` and must exactly equal the canonical models.

## Adapter Contracts

`serialization_benchmark.contracts` defines recursive `JsonValue` types, operation names, adapter metadata, and two protocols.

`PrimitiveAdapter` exposes:

```python
def dump_one(self, value: object) -> dict[str, JsonValue]: ...
def load_one(self, value: dict[str, JsonValue]) -> object: ...
def dump_many(self, values: Sequence[object]) -> list[dict[str, JsonValue]]: ...
def load_many(self, values: Sequence[dict[str, JsonValue]]) -> list[object]: ...
def normalize(self, value: object) -> Parent: ...
```

`EncodedAdapter` exposes:

```python
def encode_one(self, value: object) -> bytes: ...
def decode_one(self, value: bytes) -> object: ...
def encode_many(self, values: Sequence[object]) -> bytes: ...
def decode_many(self, value: bytes) -> list[object]: ...
def normalize(self, value: object) -> Parent: ...
```

Every adapter also declares an immutable slug, display name, supported operations, format, library version, and model strategy. `object` is intentional at this heterogeneous integration boundary; adapters recover their concrete types internally without using `Any`.

The primary model strategy is the shared stdlib dataclass wherever the library supports it. A library-native model, such as `msgspec.Struct` or `pydantic.BaseModel`, may be added later as a separately labeled strategy. Native results must never silently replace the shared-model result.

Schema objects, converters, type adapters, generated methods, encoders, and decoders are created when an adapter is constructed. Construction is outside the timed loop. A future cold-start suite may measure setup separately, but it is not part of this modernization.

## Registry and Validation

The registry contains explicit adapter instances. It does not discover modules through import side effects. Stable slugs form part of raw result names, for example `primitive.dump_one.msgspec.dataclass` and `encoded.json.encode_many.orjson.dataclass`.

Before timing, validation runs every supported operation once and checks:

- exact primitive output
- exact normalized round trips
- batch order and cardinality
- return type, including `bytes` for encoded output
- deterministic encoded payload length for the prepared fixture

Validation failures identify the adapter and operation, print the semantic difference, return a non-zero exit status, and prevent that adapter from being benchmarked. Missing registered dependencies are configuration errors and also fail fast.

## Benchmark Runner

The runner uses `pyperf.Runner.bench_time_func` so loop calibration, warmups, worker processes, and metadata collection are handled consistently while avoiding meaningful per-call harness overhead for fast serializers. Each timed function receives a loop count, performs only the target operation inside the loop, and returns elapsed `time.perf_counter()` seconds.

Prepared models, primitive inputs, encoded inputs, and adapter construction live outside the timed loop. Garbage collection remains enabled in the primary suite and is recorded as metadata. The initial design has no alternate no-GC leaderboard.

Raw output is a `pyperf` JSON file. Required metadata includes Python implementation and version, OS, architecture, CPU model, logical CPU count, benchmark package version, serializer versions, git revision, GC policy, batch size, and UTC timestamp.

The CLI exposes:

```text
serialization-benchmark validate
serialization-benchmark run primitive --output PATH
serialization-benchmark run encoded --output PATH
serialization-benchmark report RAW_JSON --markdown PATH --html PATH
```

The `run` commands always validate selected adapters first. They accept adapter and operation filters for local investigation without changing benchmark definitions.

## Result Model and Reporting

The report generator reads raw `pyperf` JSON and adapter metadata. It does not scrape terminal output. The Markdown and HTML reports group tables by tier, model strategy, format, operation, and batch size.

Every row contains library name and version, mean time per operation, standard deviation, operations per second, and sample count. Encoded rows also contain payload bytes. Relative speed may be shown only within a single table and uses that table's handwritten or stdlib baseline. There is no composite score.

Reports carry the environment metadata and a clear warning that measurements from different machines are not directly comparable. The generator uses the Python standard library and checked-in CSS rather than adding a template dependency.

## Packaging and Project Layout

The repository becomes a `uv`-managed Python project with a committed `pyproject.toml` and `uv.lock`. Runtime dependencies contain the complete active benchmark suite because `uv` resolves dependency groups together; development-only tools live in the PEP 735 `dev` group. The project requires Python `>=3.12,<3.15` and exposes the `serialization-benchmark` console script.

The target layout is:

```text
serialization_benchmark/
  __init__.py
  cli.py
  contracts.py
  fixtures.py
  registry.py
  validation.py
  runner.py
  reporting.py
  adapters/
    baselines.py
    marshmallow.py
    drf.py
    msgspec.py
    mashumaro.py
    cattrs.py
    pydantic.py
    serpyco_rs.py
    adaptix.py
    encoded_json.py
    encoded_msgpack.py
    encoded_avro.py
    encoded_pickle.py
tests/
  test_fixtures.py
  test_registry.py
  test_primitive_adapters.py
  test_encoded_adapters.py
  test_validation.py
  test_reporting.py
  test_cli.py
results/
  raw/
  reports/
```

`benchmark.py`, `data.py`, `requirements.txt`, the entire `subjects/` directory, and the existing serializer tests are removed in the atomic baseline cutover after the new baseline CLI and tests pass. Maintained framework adapters are then reintroduced under the new contracts. The Docker image copies a pinned uv binary from the official Astral image, installs from the lockfile, and uses Python 3.14 as the canonical container runtime.

## Automation and Publication

GitHub Actions replaces Travis CI and the encrypted deploy key. The baseline cutover installs the correctness workflow and removes the old publication scripts because they depend on the deleted entry point. Pages publication returns after the new runner and report generator exist. CI runs on Python 3.12, 3.13, and 3.14 and performs:

```text
uv sync --locked
uv run pytest
uv run serialization-benchmark validate
```

A minimal `pyperf` smoke invocation verifies benchmark wiring without treating shared-runner timings as a regression signal. The complete suite is manual through `workflow_dispatch` or run locally on declared hardware. Complete runs upload raw JSON and generated reports as artifacts.

GitHub Pages uses the official `configure-pages`, `upload-pages-artifact`, and `deploy-pages` actions. `deploy.sh`, `deploy-key.enc`, `.travis.yml`, and the current report concatenation script are deleted in the baseline cutover; the manual benchmark workflow becomes the only publication path once it is added.

## Testing Strategy

Tests use real serializer APIs and real encoded bytes. No serializer is mocked.

- Fixture tests prove deterministic single and batch data.
- Contract tests are parametrized over every registered adapter and supported operation.
- Validation tests use deliberately incorrect local adapters to verify diagnostic failures.
- Reporting tests consume a small checked-in `pyperf` fixture and assert table partitioning, units, payload sizes, versions, and metadata.
- CLI tests invoke the installed entry point and assert exit codes and artifact creation.
- A benchmark smoke test uses one process, one value, one warmup, and one loop to exercise orchestration without making performance assertions.

## Delivery Sequence

1. Make an atomic baseline cutover: introduce `pyproject.toml`, the package skeleton, canonical fixtures, contracts, handwritten and `dataclasses.asdict` adapters, validation, a minimal CLI, minimal uv-based README/Docker instructions, and correctness CI; simultaneously delete `benchmark.py`, `data.py`, `requirements.txt`, the entire `subjects/` package, its compatibility code, obsolete tests, Travis, and the obsolete publication scripts and key.
2. Add maintained primitive adapters and shared contract tests.
3. Add the `pyperf` runner and smoke coverage.
4. Add encoded adapters, format partitioning, and payload-size validation.
5. Add raw-result reporting and replace README methodology.
6. Extend CI with benchmark smoke coverage, add the manual benchmark and Pages workflow, and finalize Docker and documentation.
7. Run the complete canonical benchmark and publish a fresh versioned report.

Each sequence item must leave the repository runnable, keep tests passing, and be independently reviewable. The initial cutover is deliberately atomic because Toasted Marshmallow and current Marshmallow cannot safely coexist in one environment; the baseline CLI replaces the old entry point before its incompatible dependencies are removed.

## Acceptance Criteria

- Only maintained active libraries remain in code and dependency metadata.
- Every supported adapter operation passes exact semantic validation before timing.
- Primitive, JSON, MessagePack, Avro, and pickle measurements are separated.
- Single-object and 100-object batch operations have independent results.
- Schema and codec construction are outside primary timed loops.
- Raw `pyperf` JSON contains the required environment and library metadata.
- Generated Markdown and HTML can be reproduced from raw results without rerunning benchmarks.
- `uv sync --locked`, the complete test suite, validation, and the benchmark smoke run pass on Python 3.12, 3.13, and 3.14.
- Docker reproduces the Python 3.14 locked environment.
- GitHub Actions publishes Pages without an encrypted deploy key.

## References

- [pyperf runner](https://pyperf.readthedocs.io/en/latest/runner.html)
- [pyperf API](https://pyperf.readthedocs.io/en/latest/api.html)
- [Adaptix benchmark methodology](https://adaptix.readthedocs.io/en/latest/benchmarks.html)
- [msgspec usage](https://jcristharif.com/msgspec/usage.html)
- [Pydantic serialization](https://docs.pydantic.dev/latest/concepts/serialization/)
- [cattrs documentation](https://catt.rs/en/stable/)
- [serpyco-rs](https://github.com/ermakov-oleg/serpyco-rs)
- [uv project management](https://docs.astral.sh/uv/guides/projects/)
- [uv Docker integration](https://docs.astral.sh/uv/guides/integration/docker/)
- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
