import subprocess


def test_validate_command_succeeds() -> None:
    completed = subprocess.run(
        ["serialization-benchmark", "validate"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert completed.stdout.startswith("validation passed:")
