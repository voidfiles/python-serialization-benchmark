from serialization_benchmark.registry import encoded_adapters, primitive_adapters


def test_primitive_registry_order() -> None:
    assert [adapter.metadata.slug for adapter in primitive_adapters()] == [
        "handwritten",
        "dataclasses-asdict",
        "marshmallow",
        "drf",
        "cattrs",
        "mashumaro",
        "msgspec",
        "pydantic",
        "serpyco-rs",
        "adaptix",
    ]
    assert [adapter.metadata.slug for adapter in encoded_adapters()] == [
        "stdlib-json",
        "orjson",
        "msgspec-json",
        "mashumaro-json",
        "pydantic-json",
        "serpyco-rs-json",
        "msgspec-msgpack",
        "mashumaro-msgpack",
        "serpyco-rs-msgpack",
        "ormsgpack",
    ]
