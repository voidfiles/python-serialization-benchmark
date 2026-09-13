from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

from serpyco_rs import Serializer

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import Parent, normalize_parent


class SerpycoRsAdapter:
    metadata = AdapterMetadata(
        slug="serpyco-rs",
        name="serpyco-rs",
        package="serpyco-rs",
        version=version("serpyco-rs"),
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def __init__(self) -> None:
        self._one = Serializer(Parent)
        self._many = Serializer(list[Parent])

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, self._one.dump(value))

    def load_one(self, value: JsonObject) -> object:
        return self._one.load(value)

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return cast(list[JsonObject], self._many.dump(values))

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        return cast(list[object], self._many.load(values))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
