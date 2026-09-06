import pytest

from serialization_benchmark.adapters.baselines import HandwrittenAdapter
from serialization_benchmark.contracts import AdapterMetadata, JsonObject
from serialization_benchmark.fixtures import make_fixtures
from serialization_benchmark.validation import (
    AdapterValidationError,
    validate_encoded_adapter,
    validate_primitive_adapter,
)


class BrokenAdapter(HandwrittenAdapter):
    metadata = AdapterMetadata(
        slug="broken",
        name="Broken",
        package="test",
        version="1",
    )

    def dump_one(self, value: object) -> JsonObject:
        return {"wrong": True}


def test_validation_names_the_broken_operation() -> None:
    with pytest.raises(AdapterValidationError, match="broken.dump_one"):
        validate_primitive_adapter(BrokenAdapter(), make_fixtures())


class NonBytesEncodedAdapter:
    metadata = AdapterMetadata(
        slug="non-bytes",
        name="Non-bytes",
        package="test",
        version="1",
    )
    format = "json"
    operations = frozenset({"encode_one"})

    def encode_one(self, value: object) -> object:
        return bytearray(b"not bytes")

    def decode_one(self, value: bytes) -> object:
        raise AssertionError("not declared")

    def encode_many(self, values: list[object]) -> bytes:
        raise AssertionError("not declared")

    def decode_many(self, value: bytes) -> list[object]:
        raise AssertionError("not declared")

    def normalize(self, value: object) -> object:
        return value


def test_encoded_validation_rejects_non_bytes_output() -> None:
    with pytest.raises(
        AdapterValidationError,
        match="non-bytes.encode_one returned bytearray",
    ):
        validate_encoded_adapter(NonBytesEncodedAdapter(), make_fixtures())


class UnstableEncodedAdapter(NonBytesEncodedAdapter):
    metadata = AdapterMetadata(
        slug="unstable",
        name="Unstable",
        package="test",
        version="1",
    )

    def __init__(self) -> None:
        self._calls = 0

    def encode_one(self, value: object) -> bytes:
        self._calls += 1
        return b"x" * self._calls


def test_encoded_validation_rejects_unstable_payload_length() -> None:
    with pytest.raises(AdapterValidationError, match="unstable.encode_one payload_bytes"):
        validate_encoded_adapter(UnstableEncodedAdapter(), make_fixtures())
