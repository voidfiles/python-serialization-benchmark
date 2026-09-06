# Task 14: Raw Result Reporting

## Implementation

- Added `serialization_benchmark.reporting` with typed pyperf parsing, `ResultRow`, `BenchmarkReport`, deterministic partitioning, Markdown/HTML rendering, explicit metadata validation, baseline-relative columns only for handwritten primitive and stdlib-json JSON groups, and escaped HTML output.
- Added packaged report CSS and the `serialization-benchmark report RAW_JSON --markdown PATH --html PATH` CLI, including atomic UTF-8 writes and concise report failures.
- Added the deterministic checked-in pyperf fixture plus reporting and CLI integration coverage.

## RED

Command: `uv run pytest tests/test_reporting.py -v`

Output: collection failed with `ModuleNotFoundError: No module named 'serialization_benchmark.reporting'` (expected before implementation).

## GREEN and verification

- `uv run pytest tests/test_reporting.py tests/test_cli.py -v`: 6 passed.
- `uv run serialization-benchmark report tests/fixtures/pyperf-smoke.json --markdown /tmp/serialization-benchmark-report.md --html /tmp/serialization-benchmark-report.html`: created two-table Markdown and HTML artifacts without a composite score.
- A fresh runner JSON from `serialization-benchmark run ... --processes=1 --values=1 --warmups=1 --loops=1 --quiet` rendered successfully.
- Invalid pyperf JSON produced `report failed: could not load pyperf results ...` and exit status 1.
- `uv run python -m compileall -q serialization_benchmark`: passed.
- `uv run pytest -v`: 40 passed.
- `git diff --check`: passed.

## Self-review

- Rows retain the raw tier, format, operation, batch size, adapter/version/model/prerelease data, sample count, and encoded payload bytes; reports group on the full required partition key and never rank formats.
- Required report metadata fails loudly, optional CPU model is `Unknown`, raw pyperf metadata is narrowed without discarding non-primitive values, and HTML interpolation escapes all data values.
- Atomic writes use temporary sibling files and `Path.replace`; the existing run command and `run_utc` propagation are unchanged.

## Concerns

None. The report accepts both the fixture's `benchmark_version`/`gc` keys and the runner's existing `benchmark_package_version`/`gc_policy` keys so either reviewed raw result shape remains renderable.

## Fix Round 1

### Changes

- Changed the runner's global report metadata to the canonical `benchmark_version` and `gc` keys.
- Validated canonical suite metadata before timing values are read: exact string/integer types, `unit == "second"`, `gc == "enabled"`, and string-only optional CPU model data.
- Removed legacy metadata aliases and scalar coercion from required report fields; invalid prerelease metadata now raises unless it is exactly `"true"` or `"false"`.
- Translated pyperf `KeyError` and `AttributeError` loading failures into `ReportError`, keeping malformed suite JSON errors concise at the CLI.
- Added regressions for the runner contract, invalid suite metadata/unit/GC/prerelease values, and structurally invalid JSON.

### RED

Command: `uv run pytest tests/test_runner.py tests/test_reporting.py tests/test_cli.py -v`

Output: 9 failed, 9 passed. Failures confirmed missing canonical runner keys, accepted invalid unit/GC/type/legacy metadata and prerelease values, and traceback leakage for JSON without `benchmarks` and for a non-object root.

### GREEN and verification

- `uv run pytest tests/test_runner.py tests/test_reporting.py tests/test_cli.py -v`: 18 passed.
- `uv run serialization-benchmark run primitive --output /tmp/task14-round1.json --adapter handwritten --operation dump_one -- --processes=1 --values=1 --warmups=1 --loops=1 --quiet && uv run serialization-benchmark report /tmp/task14-round1.json --markdown /tmp/task14-round1.md --html /tmp/task14-round1.html`: rendered a fresh runner artifact with `Benchmark version: 0.1.0`, `GC policy: enabled`, and `Unit: second`.
- `uv run pytest -v`: 50 passed.
- `git diff --check`: passed.

### Self-review

- Canonical suite metadata is checked before `mean()`, `stdev()`, or operations/second calculations, so non-second measurements cannot be rendered as timings.
- Required display fields use exact types with no legacy fallback; extra pyperf metadata remains preserved through the existing narrowing behavior.
- Structural parser exceptions are contained by `load_report` and the CLI's existing `ReportError` branch, with focused subprocess coverage for both reported shapes.

### Concerns

None.
