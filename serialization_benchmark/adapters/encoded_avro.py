from __future__ import annotations

import json
from importlib.metadata import version
from io import BytesIO
from typing import Sequence, cast

from avro.io import BinaryDecoder, BinaryEncoder, DatumReader, DatumWriter
from avro.schema import parse

from serialization_benchmark.contracts import (
    ALL_ENCODED_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import (
    Parent,
    normalize_parent,
    parent_from_primitive,
    parent_to_primitive,
)

CHILD_SCHEMA: dict[str, object] = {
    "type": "record",
    "name": "Child",
    "fields": [
        {"name": "w", "type": "long"},
        {"name": "x", "type": "long"},
        {"name": "y", "type": "string"},
        {"name": "z", "type": "long"},
    ],
}
PARENT_SCHEMA: dict[str, object] = {
    "type": "record",
    "name": "Parent",
    "fields": [
        {"name": "foo", "type": "string"},
        {"name": "count", "type": "long"},
        {"name": "active", "type": "boolean"},
        {"name": "ratio", "type": "double"},
        {"name": "sub", "type": CHILD_SCHEMA},
        {"name": "subs", "type": {"type": "array", "items": "Child"}},
    ],
}
BATCH_SCHEMA: dict[str, object] = {"type": "array", "items": PARENT_SCHEMA}

_ONE_SCHEMA = parse(json.dumps(PARENT_SCHEMA))
_MANY_SCHEMA = parse(json.dumps(BATCH_SCHEMA))


class AvroAdapter:
    metadata = AdapterMetadata(
        slug="avro",
        name="Avro",
        package="avro",
        version=version("avro"),
    )
    format = "avro"
    operations = ALL_ENCODED_OPERATIONS

    def __init__(self) -> None:
        self._one_writer = DatumWriter(_ONE_SCHEMA)
        self._one_reader = DatumReader(_ONE_SCHEMA)
        self._many_writer = DatumWriter(_MANY_SCHEMA)
        self._many_reader = DatumReader(_MANY_SCHEMA)

    def _write(self, writer: DatumWriter, value: object) -> bytes:
        buffer = BytesIO()
        writer.write(value, BinaryEncoder(buffer))
        return buffer.getvalue()

    def encode_one(self, value: object) -> bytes:
        return self._write(self._one_writer, parent_to_primitive(cast(Parent, value)))

    def decode_one(self, value: bytes) -> object:
        raw = self._one_reader.read(BinaryDecoder(BytesIO(value)))
        return parent_from_primitive(cast(JsonObject, raw))

    def encode_many(self, values: Sequence[object]) -> bytes:
        primitives = [parent_to_primitive(cast(Parent, value)) for value in values]
        return self._write(self._many_writer, primitives)

    def decode_many(self, value: bytes) -> list[object]:
        raw = cast(list[JsonObject], self._many_reader.read(BinaryDecoder(BytesIO(value))))
        return [parent_from_primitive(item) for item in raw]

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
