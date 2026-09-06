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
