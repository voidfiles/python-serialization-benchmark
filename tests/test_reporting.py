from pathlib import Path

from serialization_benchmark.reporting import load_report, render_html, render_markdown


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
