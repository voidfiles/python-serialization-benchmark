from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

from mashumaro.codecs import BasicDecoder, BasicEncoder

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import Parent, normalize_parent


class MashumaroAdapter:
    metadata = AdapterMetadata(
        slug="mashumaro",
        name="mashumaro",
        package="mashumaro",
        version=version("mashumaro"),
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def __init__(self) -> None:
        self._one_encoder = BasicEncoder(Parent)
        self._one_decoder = BasicDecoder(Parent)
        self._many_encoder = BasicEncoder(list[Parent])
        self._many_decoder = BasicDecoder(list[Parent])

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, self._one_encoder.encode(value))

    def load_one(self, value: JsonObject) -> object:
        return self._one_decoder.decode(value)

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return cast(list[JsonObject], self._many_encoder.encode(values))

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        return self._many_decoder.decode(values)

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
