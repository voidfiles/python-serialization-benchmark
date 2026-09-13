from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

import msgspec

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import Parent, normalize_parent


class MsgspecAdapter:
    metadata = AdapterMetadata(
        slug="msgspec",
        name="msgspec",
        package="msgspec",
        version=version("msgspec"),
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, msgspec.to_builtins(value))

    def load_one(self, value: JsonObject) -> object:
        return msgspec.convert(value, type=Parent, strict=True)

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return cast(list[JsonObject], msgspec.to_builtins(values))

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        return cast(list[object], msgspec.convert(values, type=list[Parent], strict=True))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
