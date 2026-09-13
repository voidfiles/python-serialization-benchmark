from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

from adaptix import Retort

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import Parent, normalize_parent


class AdaptixAdapter:
    metadata = AdapterMetadata(
        slug="adaptix",
        name="Adaptix 3.0 beta",
        package="adaptix",
        version=version("adaptix"),
        prerelease=True,
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def __init__(self) -> None:
        self._retort = Retort()

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, self._retort.dump(value, Parent))

    def load_one(self, value: JsonObject) -> object:
        return self._retort.load(value, Parent)

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return cast(list[JsonObject], self._retort.dump(values, list[Parent]))

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        return self._retort.load(values, list[Parent])

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
