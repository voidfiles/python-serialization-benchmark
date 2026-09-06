from serialization_benchmark.contracts import PrimitiveAdapter
from serialization_benchmark.fixtures import FixtureSet, make_fixtures
from serialization_benchmark.registry import encoded_adapters, primitive_adapters


class AdapterValidationError(AssertionError):
    """An adapter result differs from the canonical fixture representation."""


def _assert_equal(operation: str, expected: object, actual: object) -> None:
    if expected != actual:
        raise AdapterValidationError(
            f"{operation}: expected={expected!r}, actual={actual!r}"
        )


def validate_primitive_adapter(
    adapter: PrimitiveAdapter,
    fixtures: FixtureSet,
) -> None:
    slug = adapter.metadata.slug
    if "dump_one" in adapter.operations:
        _assert_equal(
            f"{slug}.dump_one", fixtures.one_primitive, adapter.dump_one(fixtures.one)
        )
    if "load_one" in adapter.operations:
        loaded = adapter.normalize(adapter.load_one(fixtures.one_primitive))
        _assert_equal(f"{slug}.load_one", fixtures.one, loaded)
    if "dump_many" in adapter.operations:
        dumped = adapter.dump_many(list(fixtures.many))
        _assert_equal(f"{slug}.dump_many", list(fixtures.many_primitives), dumped)
    if "load_many" in adapter.operations:
        loaded = [
            adapter.normalize(value)
            for value in adapter.load_many(list(fixtures.many_primitives))
        ]
        _assert_equal(f"{slug}.load_many", list(fixtures.many), loaded)


def validate_all() -> None:
    fixtures = make_fixtures()
    for adapter in primitive_adapters():
        validate_primitive_adapter(adapter, fixtures)
    for adapter in encoded_adapters():
        raise NotImplementedError(
            f"encoded adapter validation is not implemented for {adapter.metadata.slug}"
        )
