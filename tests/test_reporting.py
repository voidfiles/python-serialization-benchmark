import json
from dataclasses import replace
from pathlib import Path

import pytest

from serialization_benchmark.reporting import ReportError, load_report, render_html, render_markdown


FIXTURE = Path("tests/fixtures/pyperf-smoke.json")


def test_results_preserve_partitions_and_payload_size() -> None:
    report = load_report(FIXTURE)
    rows = report.rows

    assert [(row.tier, row.format, row.operation) for row in rows] == [
        ("primitive", "", "dump_one"),
        ("encoded", "json", "encode_one"),
    ]
    assert rows[1].payload_bytes == 256
    assert rows[0].samples == 2
    assert report.metadata["git_revision"] == "fixture-revision"
    assert report.unstable_benchmark_count == 2
    assert report.benchmark_count == 2


def test_renderers_do_not_create_a_composite_score() -> None:
    report = load_report(FIXTURE)
    markdown = render_markdown(report)
    html = render_html(report)

    assert "Primitive / dump_one / batch 1" in markdown
    assert "Encoded / JSON / encode_one / batch 1" in markdown
    assert "fixture-platform" in markdown
    assert "Composite" not in markdown
    assert "<table" in html
    assert "256 B" in html


def test_renderers_disclose_comparison_limits_and_pyperf_instability() -> None:
    report = load_report(FIXTURE)

    markdown = render_markdown(report)
    html = render_html(report)

    for rendered in (markdown, html):
        assert "Results from different machines or runs are not directly comparable." in rendered
        assert "pyperf flagged 2 of 2 benchmarks as potentially unstable." in rendered
        assert "This noisy run should not be used for close comparisons." in rendered


def test_relative_values_are_speed_ratios_with_higher_values_faster() -> None:
    report = load_report(FIXTURE)
    baseline = report.rows[0]
    faster = replace(
        baseline,
        adapter_slug="faster",
        adapter_name="Faster",
        mean_seconds=baseline.mean_seconds / 2,
        operations_per_second=baseline.operations_per_second * 2,
    )
    comparison = replace(report, rows=(baseline, faster))

    markdown = render_markdown(comparison)
    html = render_html(comparison)

    assert "Speed vs baseline (higher is faster)" in markdown
    assert "Speed vs baseline (higher is faster)" in html
    assert "| Faster |" in markdown
    assert "| 2.00x |" in markdown
    assert "<td>Faster</td>" in html
    assert "<td>2.00x</td>" in html
    assert "Relative" not in markdown
    assert "Relative" not in html


@pytest.mark.parametrize(
    ("metadata_updates", "missing_metadata", "expected_key"),
    [
        ({"unit": "byte"}, (), "unit"),
        ({"gc": "disabled"}, (), "gc"),
        ({"cpu_count": "8"}, (), "cpu_count"),
        ({"benchmark_package_version": "0.1.0"}, ("benchmark_version",), "benchmark_version"),
        ({"gc_policy": "enabled"}, ("gc",), "gc"),
    ],
)
def test_load_report_rejects_noncanonical_or_invalid_suite_metadata(
    tmp_path: Path,
    metadata_updates: dict[str, str],
    missing_metadata: tuple[str, ...],
    expected_key: str,
) -> None:
    suite = json.loads(FIXTURE.read_text())
    for key in missing_metadata:
        del suite["metadata"][key]
    suite["metadata"].update(metadata_updates)
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps(suite))

    with pytest.raises(ReportError, match=expected_key):
        load_report(invalid)


@pytest.mark.parametrize("prerelease", ["unknown", True])
def test_load_report_rejects_invalid_prerelease_values(tmp_path: Path, prerelease: str | bool) -> None:
    suite = json.loads(FIXTURE.read_text())
    suite["metadata"]["prerelease"] = prerelease
    invalid = tmp_path / "invalid-prerelease.json"
    invalid.write_text(json.dumps(suite))

    with pytest.raises(ReportError, match="prerelease"):
        load_report(invalid)


@pytest.mark.parametrize(
    ("benchmark_index", "metadata_updates", "missing_metadata", "expected_key"),
    [
        (0, {"tier": "raw"}, (), "tier"),
        (0, {"operation": "encode_one"}, (), "operation"),
        (1, {"operation": "dump_one"}, (), "operation"),
        (1, {"format": "yaml"}, (), "format"),
        (1, {}, ("format",), "format"),
        (1, {"encoded_format": "json"}, ("format",), "format"),
        (0, {"format": "json"}, (), "format"),
        (0, {"payload_bytes": 256}, (), "payload_bytes"),
        (1, {}, ("payload_bytes",), "payload_bytes"),
        (1, {"payload_bytes": 0}, (), "payload_bytes"),
        (1, {"payload_bytes": -1}, (), "payload_bytes"),
        (1, {"payload_bytes": "256"}, (), "payload_bytes"),
        (1, {"name": "encoded.json.encode_one.wrong.dataclass"}, (), "name"),
    ],
)
def test_load_report_rejects_invalid_tier_aware_row_metadata(
    tmp_path: Path,
    benchmark_index: int,
    metadata_updates: dict[str, str | int],
    missing_metadata: tuple[str, ...],
    expected_key: str,
) -> None:
    suite = json.loads(FIXTURE.read_text())
    metadata = suite["benchmarks"][benchmark_index]["metadata"]
    for key in missing_metadata:
        del metadata[key]
    metadata.update(metadata_updates)
    invalid = tmp_path / "invalid-row.json"
    invalid.write_text(json.dumps(suite))

    with pytest.raises(ReportError, match=expected_key):
        load_report(invalid)


@pytest.mark.parametrize("batch_size", [0, -1, "1"])
def test_load_report_rejects_nonpositive_or_noninteger_batch_size(
    tmp_path: Path,
    batch_size: int | str,
) -> None:
    suite = json.loads(FIXTURE.read_text())
    suite["metadata"]["batch_size"] = batch_size
    invalid = tmp_path / "invalid-batch-size.json"
    invalid.write_text(json.dumps(suite))

    with pytest.raises(ReportError, match="batch_size"):
        load_report(invalid)
