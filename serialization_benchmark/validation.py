from serialization_benchmark.contracts import EncodedAdapter, PrimitiveAdapter
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


def _assert_bytes(operation: str, value: object) -> bytes:
    if type(value) is not bytes:
        raise AdapterValidationError(f"{operation} returned {type(value).__name__}")
    return value


def _assert_stable_payload_length(
    operation: str,
    first: bytes,
    second: object,
) -> None:
    repeated = _assert_bytes(operation, second)
    _assert_equal(f"{operation} payload_bytes", len(first), len(repeated))


def validate_encoded_adapter(
    adapter: EncodedAdapter,
    fixtures: FixtureSet,
) -> None:
    slug = adapter.metadata.slug
    encoded_one: bytes | None = None
    encoded_many: bytes | None = None

    if "encode_one" in adapter.operations or "decode_one" in adapter.operations:
        encoded_one = _assert_bytes(
            f"{slug}.encode_one", adapter.encode_one(fixtures.one)
        )
        _assert_stable_payload_length(
            f"{slug}.encode_one", encoded_one, adapter.encode_one(fixtures.one)
        )
    if "decode_one" in adapter.operations:
        if encoded_one is None:
            raise AssertionError("encoded one payload was not prepared")
        decoded_one = adapter.normalize(adapter.decode_one(encoded_one))
        _assert_equal(f"{slug}.decode_one", fixtures.one, decoded_one)

    if "encode_many" in adapter.operations or "decode_many" in adapter.operations:
        values = list(fixtures.many)
        encoded_many = _assert_bytes(
            f"{slug}.encode_many", adapter.encode_many(values)
        )
        _assert_stable_payload_length(
            f"{slug}.encode_many", encoded_many, adapter.encode_many(values)
        )
    if "decode_many" in adapter.operations:
        if encoded_many is None:
            raise AssertionError("encoded many payload was not prepared")
        decoded_many = [
            adapter.normalize(value) for value in adapter.decode_many(encoded_many)
        ]
        _assert_equal(f"{slug}.decode_many", list(fixtures.many), decoded_many)


def validate_all() -> None:
    fixtures = make_fixtures()
    for adapter in primitive_adapters():
        validate_primitive_adapter(adapter, fixtures)
    for adapter in encoded_adapters():
        validate_encoded_adapter(adapter, fixtures)
