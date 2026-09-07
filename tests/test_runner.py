from serialization_benchmark.fixtures import make_fixtures
from serialization_benchmark.runner import _global_metadata, build_encoded_cases, build_primitive_cases


def test_global_metadata_uses_canonical_report_keys() -> None:
    metadata = _global_metadata("2026-09-06T21:00:00+00:00")

    assert metadata["benchmark_version"]
    assert metadata["gc"] == "enabled"
    assert "benchmark_package_version" not in metadata
    assert "gc_policy" not in metadata


def test_primitive_cases_are_partitioned_by_operation() -> None:
    cases = build_primitive_cases(make_fixtures())
    names = {case.name for case in cases}

    assert "primitive.dump_one.handwritten.dataclass" in names
    assert "primitive.load_one.handwritten.dataclass" in names
    assert "primitive.dump_many.dataclasses-asdict.dataclass" in names
    assert "primitive.load_one.dataclasses-asdict.dataclass" not in names
    assert all(case.metadata["gc"] == "enabled" for case in cases)


def test_all_encoded_cases_include_their_prepared_payload_size() -> None:
    cases = build_encoded_cases(make_fixtures())

    assert all(type(case.metadata["payload_bytes"]) is int for case in cases)
    assert all(case.metadata["payload_bytes"] > 0 for case in cases)

    cases_by_name = {case.name: case for case in cases}
    assert cases_by_name["encoded.encode_one.stdlib-json.dataclass"].metadata[
        "payload_bytes"
    ] == cases_by_name["encoded.decode_one.stdlib-json.dataclass"].metadata["payload_bytes"]
    assert cases_by_name["encoded.encode_many.stdlib-json.dataclass"].metadata[
        "payload_bytes"
    ] == cases_by_name["encoded.decode_many.stdlib-json.dataclass"].metadata[
        "payload_bytes"
    ]
