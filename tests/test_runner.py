from serialization_benchmark.fixtures import make_fixtures
from serialization_benchmark.runner import build_primitive_cases


def test_primitive_cases_are_partitioned_by_operation() -> None:
    cases = build_primitive_cases(make_fixtures())
    names = {case.name for case in cases}

    assert "primitive.dump_one.handwritten.dataclass" in names
    assert "primitive.load_one.handwritten.dataclass" in names
    assert "primitive.dump_many.dataclasses-asdict.dataclass" in names
    assert "primitive.load_one.dataclasses-asdict.dataclass" not in names
    assert all(case.metadata["gc"] == "enabled" for case in cases)
