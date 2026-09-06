from serialization_benchmark.registry import encoded_adapters, primitive_adapters


def test_primitive_registry_order() -> None:
    assert [adapter.metadata.slug for adapter in primitive_adapters()] == [
        "handwritten",
        "dataclasses-asdict",
    ]
    assert encoded_adapters() == ()
