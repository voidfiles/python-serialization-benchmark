import subprocess
from pathlib import Path

import pyperf
import pytest


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
    raw_result = output.read_text()
    assert '"hostname"' not in raw_result
    assert '"python_executable"' not in raw_result
    assert Path(__file__).parents[1].as_posix() not in raw_result


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


@pytest.mark.parametrize(
    ("html_name", "primitive_href", "encoded_href"),
    [
        ("index.html", "index.html", "encoded.html"),
        ("encoded.html", "index.html", "encoded.html"),
        (
            "2026-09-06-cpython-3.14-primitive.html",
            "2026-09-06-cpython-3.14-primitive.html",
            "2026-09-06-cpython-3.14-encoded.html",
        ),
        (
            "2026-09-06-cpython-3.14-encoded.html",
            "2026-09-06-cpython-3.14-primitive.html",
            "2026-09-06-cpython-3.14-encoded.html",
        ),
    ],
)
def test_report_command_links_to_sibling_report_names(
    tmp_path: Path,
    html_name: str,
    primitive_href: str,
    encoded_href: str,
) -> None:
    html = tmp_path / html_name

    completed = subprocess.run(
        [
            "serialization-benchmark",
            "report",
            "tests/fixtures/pyperf-smoke.json",
            "--markdown",
            str(tmp_path / "report.md"),
            "--html",
            str(html),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    contents = html.read_text()
    assert f'href="{primitive_href}">Primitive results</a>' in contents
    assert f'href="{encoded_href}">Encoded results</a>' in contents


@pytest.mark.parametrize("contents", ['{"version": "1.0"}', "[]"])
def test_report_command_handles_structurally_invalid_pyperf_json(
    tmp_path: Path,
    contents: str,
) -> None:
    raw_json = tmp_path / "invalid.json"
    raw_json.write_text(contents)

    completed = subprocess.run(
        [
            "serialization-benchmark",
            "report",
            str(raw_json),
            "--markdown",
            str(tmp_path / "report.md"),
            "--html",
            str(tmp_path / "report.html"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert completed.stderr.startswith("report failed:")
    assert "Traceback" not in completed.stderr


@pytest.mark.parametrize(
    "arguments",
    [
        ["validate", "--unknown"],
        [
            "report",
            "tests/fixtures/pyperf-smoke.json",
            "--markdown",
            "unused.md",
            "--html",
            "unused.html",
            "--unknown",
        ],
    ],
)
def test_non_run_commands_reject_unknown_arguments(arguments: list[str]) -> None:
    completed = subprocess.run(
        ["serialization-benchmark", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "unrecognized arguments: --unknown" in completed.stderr
