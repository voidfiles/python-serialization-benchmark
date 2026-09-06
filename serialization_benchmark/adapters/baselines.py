from __future__ import annotations

import platform
from dataclasses import asdict, dataclass
from typing import Sequence, cast

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
    PrimitiveOperation,
)
from serialization_benchmark.fixtures import (
    Parent,
    normalize_parent,
    parent_from_primitive,
    parent_to_primitive,
)


@dataclass(frozen=True)
class HandwrittenAdapter:
    metadata = AdapterMetadata(
        slug="handwritten",
        name="Handwritten",
        package="python",
        version=platform.python_version(),
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def dump_one(self, value: object) -> JsonObject:
        return parent_to_primitive(cast(Parent, value))

    def load_one(self, value: JsonObject) -> object:
        return parent_from_primitive(value)

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return [parent_to_primitive(cast(Parent, value)) for value in values]

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        return [parent_from_primitive(value) for value in values]

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)


@dataclass(frozen=True)
class DataclassesAsdictAdapter:
    metadata = AdapterMetadata(
        slug="dataclasses-asdict",
        name="dataclasses.asdict",
        package="python",
        version=platform.python_version(),
    )
    operations: frozenset[PrimitiveOperation] = frozenset({"dump_one", "dump_many"})

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, asdict(cast(Parent, value)))

    def load_one(self, value: JsonObject) -> object:
        raise NotImplementedError("dataclasses.asdict does not load values")

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return [cast(JsonObject, asdict(cast(Parent, value))) for value in values]

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        raise NotImplementedError("dataclasses.asdict does not load values")

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
