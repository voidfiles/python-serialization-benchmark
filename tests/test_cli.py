import subprocess
from pathlib import Path

import pyperf


def test_validate_command_succeeds() -> None:
    completed = subprocess.run(
        ["serialization-benchmark", "validate"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert completed.stdout.startswith("validation passed:")


def test_run_command_writes_selected_primitive_benchmark(tmp_path: Path) -> None:
    output = tmp_path / "primitive.json"

    completed = subprocess.run(
        [
            "serialization-benchmark",
            "run",
            "primitive",
            "--output",
            str(output),
            "--adapter",
            "handwritten",
            "--operation",
            "dump_one",
            "--",
            "--processes=1",
            "--values=1",
            "--warmups=1",
            "--loops=1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert output.exists()


def test_run_command_retains_common_run_timestamp_across_workers(
    tmp_path: Path,
) -> None:
    output = tmp_path / "primitive.json"

    completed = subprocess.run(
        [
            "serialization-benchmark",
            "run",
            "primitive",
            "--output",
            str(output),
            "--adapter",
            "handwritten",
            "--operation",
            "dump_one",
            "--",
            "--processes=2",
            "--values=1",
            "--warmups=1",
            "--loops=1",
            "--quiet",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert pyperf.Benchmark.load(str(output)).get_metadata()["run_utc"]


def test_report_command_writes_partitioned_artifacts(tmp_path: Path) -> None:
    markdown = tmp_path / "nested" / "report.md"
    html = tmp_path / "nested" / "report.html"

    completed = subprocess.run(
        [
            "serialization-benchmark",
            "report",
            "tests/fixtures/pyperf-smoke.json",
            "--markdown",
            str(markdown),
            "--html",
            str(html),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert markdown.exists()
    assert html.exists()
    assert markdown.read_text().count("| Version |") == 2
    assert "Composite" not in markdown.read_text()
    assert html.read_text().count("<table") == 2
