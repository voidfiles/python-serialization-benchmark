import json
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
