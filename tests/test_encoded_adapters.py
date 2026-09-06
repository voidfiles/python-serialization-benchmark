import pytest

from serialization_benchmark.contracts import EncodedAdapter
from serialization_benchmark.fixtures import make_fixtures
from serialization_benchmark.registry import encoded_adapters
from serialization_benchmark.validation import validate_encoded_adapter


@pytest.mark.parametrize(
    "adapter",
    encoded_adapters(),
    ids=lambda adapter: adapter.metadata.slug,
)
def test_registered_encoded_adapter_is_semantically_correct(
    adapter: EncodedAdapter,
) -> None:
    validate_encoded_adapter(adapter, make_fixtures())


def test_json_adapters_are_registered() -> None:
    assert [
        adapter.metadata.slug
        for adapter in encoded_adapters()
        if adapter.format == "json"
    ] == [
        "stdlib-json",
        "orjson",
        "msgspec-json",
        "mashumaro-json",
        "pydantic-json",
        "serpyco-rs-json",
    ]


def test_messagepack_adapters_are_registered() -> None:
    assert [
        adapter.metadata.slug
        for adapter in encoded_adapters()
        if adapter.format == "messagepack"
    ] == [
        "msgspec-msgpack",
        "mashumaro-msgpack",
        "serpyco-rs-msgpack",
        "ormsgpack",
    ]
