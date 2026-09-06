from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

from pydantic import TypeAdapter

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import Parent, normalize_parent


class PydanticAdapter:
    metadata = AdapterMetadata(
        slug="pydantic",
        name="Pydantic v2",
        package="pydantic",
        version=version("pydantic"),
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def __init__(self) -> None:
        self._one = TypeAdapter(Parent)
        self._many = TypeAdapter(list[Parent])

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, self._one.dump_python(value, mode="json"))

    def load_one(self, value: JsonObject) -> object:
        return self._one.validate_python(value)

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return cast(list[JsonObject], self._many.dump_python(values, mode="json"))

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        return cast(list[object], self._many.validate_python(values))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
