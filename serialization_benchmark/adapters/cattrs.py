from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

from cattrs import Converter

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import Parent, normalize_parent


class CattrsAdapter:
    metadata = AdapterMetadata(
        slug="cattrs",
        name="cattrs",
        package="cattrs",
        version=version("cattrs"),
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def __init__(self) -> None:
        converter = Converter()
        self._dump_one = converter.get_unstructure_hook(Parent)
        self._load_one = converter.get_structure_hook(Parent)
        self._dump_many = converter.get_unstructure_hook(list[Parent])
        self._load_many = converter.get_structure_hook(list[Parent])

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, self._dump_one(value))

    def load_one(self, value: JsonObject) -> object:
        return self._load_one(value, Parent)

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return cast(list[JsonObject], self._dump_many(values))

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        return self._load_many(values, list[Parent])

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
