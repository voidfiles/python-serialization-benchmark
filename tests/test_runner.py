from serialization_benchmark.fixtures import make_fixtures
from serialization_benchmark.runner import build_encoded_cases, build_primitive_cases


def test_primitive_cases_are_partitioned_by_operation() -> None:
    cases = build_primitive_cases(make_fixtures())
    names = {case.name for case in cases}

    assert "primitive.dump_one.handwritten.dataclass" in names
    assert "primitive.load_one.handwritten.dataclass" in names
    assert "primitive.dump_many.dataclasses-asdict.dataclass" in names
    assert "primitive.load_one.dataclasses-asdict.dataclass" not in names
    assert all(case.metadata["gc"] == "enabled" for case in cases)


def test_encoded_decode_cases_include_prepared_payload_size() -> None:
    cases = build_encoded_cases(make_fixtures())

    decode_cases = [
        case
        for case in cases
        if case.metadata["format"] == "json"
        and case.metadata["operation"] in {"decode_one", "decode_many"}
    ]

    assert len(decode_cases) == 12
    assert all(case.metadata["format"] == "json" for case in decode_cases)
    assert all(type(case.metadata["payload_bytes"]) is int for case in decode_cases)
    assert all(case.metadata["payload_bytes"] > 0 for case in decode_cases)
