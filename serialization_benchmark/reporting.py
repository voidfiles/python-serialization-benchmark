from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from html import escape
from importlib.resources import files
from pathlib import Path
from typing import TypeAlias

import pyperf
from pyperf._cli import format_checks

from serialization_benchmark.contracts import (
    ALL_ENCODED_FORMATS,
    ALL_ENCODED_OPERATIONS,
    ALL_PRIMITIVE_OPERATIONS,
)


MetadataValue: TypeAlias = str | int | float | bool


class ReportError(ValueError):
    """Raised when a pyperf result cannot be rendered faithfully."""


@dataclass(frozen=True)
class ResultRow:
    tier: str
    format: str
    operation: str
    batch_size: int
    adapter_slug: str
    adapter_name: str
    library_version: str
    model_strategy: str
    prerelease: bool
    mean_seconds: float
    stdev_seconds: float
    operations_per_second: float
    samples: int
    payload_bytes: int | None


@dataclass(frozen=True)
class BenchmarkReport:
    rows: tuple[ResultRow, ...]
    metadata: dict[str, MetadataValue]
    unstable_benchmark_count: int
    benchmark_count: int


_UNSTABLE_WARNING = "WARNING: the benchmark result may be unstable"
_SPEED_HEADER = "Speed vs baseline (higher is faster)"


def load_report(path: Path) -> BenchmarkReport:
    try:
        suite = pyperf.BenchmarkSuite.load(str(path))
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as error:
        raise ReportError(f"could not load pyperf results from {path}: {error}") from error

    suite_metadata = suite.get_metadata()
    _validate_suite_metadata(suite_metadata)
    rows: list[ResultRow] = []
    unstable_benchmark_count = 0
    for benchmark in suite.get_benchmarks():
        metadata = benchmark.get_metadata()
        benchmark_name = benchmark.get_name()
        tier, encoded_format, operation, batch_size, payload_bytes = _validate_row_metadata(
            metadata,
            benchmark_name,
        )
        mean = benchmark.mean()
        sample_count = benchmark.get_nvalue()
        if _UNSTABLE_WARNING in format_checks(benchmark):
            unstable_benchmark_count += 1
        rows.append(
            ResultRow(
                tier=tier,
                format=encoded_format,
                operation=operation,
                batch_size=batch_size,
                adapter_slug=_required_str(metadata, "adapter_slug", benchmark_name),
                adapter_name=_required_str(metadata, "adapter_name", benchmark_name),
                library_version=_required_str(metadata, "library_version", benchmark_name),
                model_strategy=_required_str(metadata, "model_strategy", benchmark_name),
                prerelease=_required_prerelease(metadata, benchmark_name),
                mean_seconds=mean,
                stdev_seconds=benchmark.stdev() if sample_count > 1 else 0.0,
                operations_per_second=1.0 / mean,
                samples=sample_count,
                payload_bytes=payload_bytes,
            )
        )
    return BenchmarkReport(
        rows=tuple(sorted(rows, key=_result_sort_key)),
        metadata=_narrow_metadata(suite_metadata),
        unstable_benchmark_count=unstable_benchmark_count,
        benchmark_count=len(rows),
    )


def render_markdown(report: BenchmarkReport) -> str:
    lines = [
        "# Serialization benchmark results",
        "",
        f"> **Comparison warning:** {_comparison_warning(report)}",
        "",
        "## Environment",
        "",
    ]
    lines.extend(f"- {label}: {_markdown(value)}" for label, value in _environment_rows(report.metadata))
    for group_key, rows in _groups(report.rows):
        lines.extend(("", f"## {_group_title(group_key)}", ""))
        lines.extend(_markdown_table(group_key, rows))
    return "\n".join(lines) + "\n"


def render_html(
    report: BenchmarkReport,
    *,
    primitive_href: str = "index.html",
    encoded_href: str = "encoded.html",
) -> str:
    environment = "\n".join(
        f"<dt>{escape(label)}</dt><dd>{escape(value)}</dd>"
        for label, value in _environment_rows(report.metadata)
    )
    sections = "\n".join(_html_table(group_key, rows) for group_key, rows in _groups(report.rows))
    css = files("serialization_benchmark").joinpath("report.css").read_text(encoding="utf-8")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Serialization benchmark results</title>
<style>{css}</style>
</head>
<body>
<main>
<h1>Serialization benchmark results</h1>
<nav aria-label="Benchmark reports"><a href="{escape(primitive_href, quote=True)}">Primitive results</a> <a href="{escape(encoded_href, quote=True)}">Encoded results</a></nav>
<aside class="warning" role="note"><h2>Comparison warning</h2><p>{escape(_comparison_warning(report))}</p></aside>
<section><h2>Environment</h2><dl>{environment}</dl></section>
{sections}
</main>
</body>
</html>
"""


def _comparison_warning(report: BenchmarkReport) -> str:
    warning = (
        "Results from different machines or runs are not directly comparable. "
        f"pyperf flagged {report.unstable_benchmark_count} of "
        f"{report.benchmark_count} benchmarks as potentially unstable."
    )
    if report.unstable_benchmark_count:
        warning += " This noisy run should not be used for close comparisons."
    return warning


def _validate_row_metadata(
    metadata: dict[str, object],
    benchmark: str,
) -> tuple[str, str, str, int, int | None]:
    tier = _required_str(metadata, "tier", benchmark)
    operation = _required_str(metadata, "operation", benchmark)
    batch_size = _required_positive_int(metadata, "batch_size", benchmark)
    adapter_slug = _required_str(metadata, "adapter_slug", benchmark)
    model_strategy = _required_str(metadata, "model_strategy", benchmark)

    if "encoded_format" in metadata:
        raise ReportError(
            f"benchmark {benchmark!r} uses noncanonical metadata 'encoded_format'; use 'format'"
        )

    if tier == "primitive":
        if operation not in ALL_PRIMITIVE_OPERATIONS:
            raise ReportError(
                f"benchmark {benchmark!r} has invalid primitive operation metadata {operation!r}"
            )
        if "format" in metadata:
            raise ReportError(f"primitive benchmark {benchmark!r} must not define metadata 'format'")
        if "payload_bytes" in metadata:
            raise ReportError(
                f"primitive benchmark {benchmark!r} must not define metadata 'payload_bytes'"
            )
        encoded_format = ""
        payload_bytes = None
        expected_name = ".".join((tier, operation, adapter_slug, model_strategy))
    elif tier == "encoded":
        encoded_format = _required_str(metadata, "format", benchmark)
        if encoded_format not in ALL_ENCODED_FORMATS:
            raise ReportError(
                f"benchmark {benchmark!r} has invalid encoded format metadata {encoded_format!r}"
            )
        if operation not in ALL_ENCODED_OPERATIONS:
            raise ReportError(
                f"benchmark {benchmark!r} has invalid encoded operation metadata {operation!r}"
            )
        payload_bytes = _required_positive_int(metadata, "payload_bytes", benchmark)
        expected_name = ".".join(
            (tier, encoded_format, operation, adapter_slug, model_strategy)
        )
    else:
        raise ReportError(f"benchmark {benchmark!r} has invalid tier metadata {tier!r}")

    if benchmark != expected_name:
        raise ReportError(
            f"benchmark name {benchmark!r} is inconsistent with metadata; expected {expected_name!r}"
        )
    return tier, encoded_format, operation, batch_size, payload_bytes


def _required_str(metadata: dict[str, object], key: str, benchmark: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str):
        raise ReportError(f"benchmark {benchmark!r} has missing or non-string metadata {key!r}")
    return value


def _required_int(metadata: dict[str, object], key: str, benchmark: str) -> int:
    value = metadata.get(key)
    if type(value) is not int:
        raise ReportError(f"benchmark {benchmark!r} has missing or non-integer metadata {key!r}")
    return value


def _required_positive_int(metadata: dict[str, object], key: str, benchmark: str) -> int:
    value = _required_int(metadata, key, benchmark)
    if value <= 0:
        raise ReportError(f"benchmark {benchmark!r} has nonpositive metadata {key!r}")
    return value


def _required_prerelease(metadata: dict[str, object], benchmark: str) -> bool:
    value = _required_str(metadata, "prerelease", benchmark)
    if value not in {"true", "false"}:
        raise ReportError(f"benchmark {benchmark!r} has invalid prerelease metadata {value!r}")
    return value == "true"


def _narrow_metadata(metadata: dict[str, object]) -> dict[str, MetadataValue]:
    narrowed: dict[str, MetadataValue] = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            narrowed[key] = value
        else:
            narrowed[key] = pyperf.format_metadata(key, value)
    return narrowed


def _validate_suite_metadata(metadata: dict[str, object]) -> None:
    required_strings = (
        "python_version",
        "python_implementation",
        "platform",
        "git_revision",
        "benchmark_version",
        "gc",
        "run_utc",
        "unit",
    )
    for key in required_strings:
        _required_str(metadata, key, "suite")
    _required_int(metadata, "cpu_count", "suite")
    if "cpu_model_name" in metadata:
        _required_str(metadata, "cpu_model_name", "suite")
    if metadata["unit"] != "second":
        raise ReportError("suite metadata 'unit' must be 'second'")
    if metadata["gc"] != "enabled":
        raise ReportError("suite metadata 'gc' must be 'enabled'")


def _result_sort_key(row: ResultRow) -> tuple[int, str, str, int, str, str]:
    tier_order = {"primitive": 0, "encoded": 1}
    return (
        tier_order.get(row.tier, 2),
        row.format,
        row.operation,
        row.batch_size,
        row.model_strategy,
        row.adapter_slug,
    )


GroupKey: TypeAlias = tuple[str, str, str, int, str]


def _groups(rows: tuple[ResultRow, ...]) -> tuple[tuple[GroupKey, tuple[ResultRow, ...]], ...]:
    grouped: defaultdict[GroupKey, list[ResultRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.tier, row.format, row.operation, row.batch_size, row.model_strategy)].append(row)
    return tuple(
        (key, tuple(sorted(group_rows, key=lambda row: row.adapter_slug)))
        for key, group_rows in sorted(grouped.items(), key=lambda item: _group_sort_key(item[0]))
    )


def _group_sort_key(key: GroupKey) -> tuple[int, str, str, int, str]:
    tier, encoded_format, operation, batch_size, model_strategy = key
    return ({"primitive": 0, "encoded": 1}.get(tier, 2), encoded_format, operation, batch_size, model_strategy)


def _group_title(key: GroupKey) -> str:
    tier, encoded_format, operation, batch_size, model_strategy = key
    parts = [tier.capitalize()]
    if encoded_format:
        parts.append(encoded_format.upper())
    parts.extend((operation, f"batch {batch_size}", model_strategy))
    return " / ".join(parts)


def _environment_rows(metadata: dict[str, MetadataValue]) -> tuple[tuple[str, str], ...]:
    return (
        ("Python", _required_metadata(metadata, "python_version") + f" ({_required_metadata(metadata, 'python_implementation')})"),
        ("Platform", _required_metadata(metadata, "platform")),
        ("CPU model", _optional_metadata(metadata, "cpu_model_name") or "Unknown"),
        ("CPU count", _required_integer_metadata(metadata, "cpu_count")),
        ("Git revision", _required_metadata(metadata, "git_revision")),
        ("Benchmark version", _required_metadata(metadata, "benchmark_version")),
        ("GC policy", _required_metadata(metadata, "gc")),
        ("Run UTC", _required_metadata(metadata, "run_utc")),
        ("Unit", _required_metadata(metadata, "unit")),
    )


def _required_metadata(metadata: dict[str, MetadataValue], key: str) -> str:
    value = metadata.get(key)
    if type(value) is not str:
        raise ReportError(f"report metadata has missing or non-string value {key!r}")
    return value


def _required_integer_metadata(metadata: dict[str, MetadataValue], key: str) -> str:
    value = metadata.get(key)
    if type(value) is not int:
        raise ReportError(f"report metadata has missing or non-integer value {key!r}")
    return str(value)


def _optional_metadata(metadata: dict[str, MetadataValue], key: str) -> str | None:
    value = metadata.get(key)
    if value is None:
        return None
    if type(value) is not str:
        raise ReportError(f"report metadata has non-string value {key!r}")
    return value


def _markdown_table(key: GroupKey, rows: tuple[ResultRow, ...]) -> list[str]:
    has_relative = _baseline(key, rows) is not None
    headers = ["Adapter", "Version", "Mean", "Std dev", "Operations/s", "Samples", "Prerelease"]
    if key[0] == "encoded":
        headers.append("Payload")
    if has_relative:
        headers.append(_SPEED_HEADER)
    baseline = _baseline(key, rows)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        values = _table_values(row, baseline, key[0] == "encoded")
        lines.append("| " + " | ".join(_markdown(value) for value in values) + " |")
    return lines


def _html_table(key: GroupKey, rows: tuple[ResultRow, ...]) -> str:
    baseline = _baseline(key, rows)
    headers = ["Adapter", "Version", "Mean", "Std dev", "Operations/s", "Samples", "Prerelease"]
    if key[0] == "encoded":
        headers.append("Payload")
    if baseline is not None:
        headers.append(_SPEED_HEADER)
    header_html = "".join(f"<th scope=\"col\">{escape(header)}</th>" for header in headers)
    rows_html = "\n".join(
        "<tr>" + "".join(f"<td>{escape(value)}</td>" for value in _table_values(row, baseline, key[0] == "encoded")) + "</tr>"
        for row in rows
    )
    return f"<section><h2>{escape(_group_title(key))}</h2><table><thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table></section>"


def _baseline(key: GroupKey, rows: tuple[ResultRow, ...]) -> ResultRow | None:
    tier, encoded_format, _, _, _ = key
    baseline_slug = "handwritten" if tier == "primitive" else "stdlib-json" if encoded_format == "json" else None
    if baseline_slug is None:
        return None
    return next((row for row in rows if row.adapter_slug == baseline_slug), None)


def _table_values(row: ResultRow, baseline: ResultRow | None, encoded: bool) -> list[str]:
    values = [
        row.adapter_name,
        row.library_version,
        _format_seconds(row.mean_seconds),
        _format_seconds(row.stdev_seconds),
        f"{row.operations_per_second:.6g}",
        str(row.samples),
        "pre-release" if row.prerelease else "",
    ]
    if encoded:
        values.append(_format_bytes(row.payload_bytes))
    if baseline is not None:
        values.append(f"{baseline.mean_seconds / row.mean_seconds:.2f}x")
    return values


def _format_seconds(seconds: float) -> str:
    if seconds < 0.000001:
        return f"{seconds * 1_000_000_000:.6g} ns"
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.6g} µs"
    if seconds < 1:
        return f"{seconds * 1_000:.6g} ms"
    return f"{seconds:.6g} s"


def _format_bytes(payload_bytes: int | None) -> str:
    return "" if payload_bytes is None else f"{payload_bytes} B"


def _markdown(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")
