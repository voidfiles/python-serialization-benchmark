import json
from pathlib import Path

import pyperf

from serialization_benchmark.publication import sanitize_raw_result


FIXTURE = Path("tests/fixtures/pyperf-smoke.json")


def test_sanitize_raw_result_removes_private_environment_fields_and_remains_loadable(
    tmp_path: Path,
) -> None:
    result = json.loads(FIXTURE.read_text())
    result["metadata"]["hostname"] = "developer-workstation.local"
    result["metadata"]["python_executable"] = "/Users/developer/project/.venv/bin/python"
    result["benchmarks"][0]["runs"][0]["metadata"] = {
        "hostname": "nested-workstation.local",
        "python_executable": "/Users/developer/project/.venv/bin/python",
    }
    published = tmp_path / "published.json"
    published.write_text(json.dumps(result))

    sanitize_raw_result(published)
    first_publication = published.read_bytes()
    sanitized = json.loads(first_publication)

    assert "hostname" not in first_publication.decode()
    assert "python_executable" not in first_publication.decode()
    assert "/Users/developer" not in first_publication.decode()
    assert sanitized["benchmarks"][0]["runs"][0]["metadata"] == {}
    assert len(pyperf.BenchmarkSuite.load(str(published))) == 2

    sanitize_raw_result(published)

    assert published.read_bytes() == first_publication
