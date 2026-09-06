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
