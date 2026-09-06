from __future__ import annotations

import json
import platform
from importlib.metadata import version
from typing import Sequence, cast

import msgspec
import orjson
from mashumaro.codecs.json import JSONDecoder, JSONEncoder
from pydantic import TypeAdapter
from serpyco_rs import JSON, Serializer

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


class StdlibJsonAdapter:
    metadata = AdapterMetadata(
        slug="stdlib-json",
        name="stdlib json",
        package="python",
        version=platform.python_version(),
    )
    format = "json"
    operations = ALL_ENCODED_OPERATIONS

    def encode_one(self, value: object) -> bytes:
        return json.dumps(
            parent_to_primitive(cast(Parent, value)), separators=(",", ":")
        ).encode("utf-8")

    def decode_one(self, value: bytes) -> object:
        return parent_from_primitive(cast(JsonObject, json.loads(value)))

    def encode_many(self, values: Sequence[object]) -> bytes:
        primitives = [parent_to_primitive(cast(Parent, value)) for value in values]
        return json.dumps(primitives, separators=(",", ":")).encode("utf-8")

    def decode_many(self, value: bytes) -> list[object]:
        decoded = cast(list[JsonObject], json.loads(value))
        return [parent_from_primitive(item) for item in decoded]

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)


class OrjsonAdapter:
    metadata = AdapterMetadata(
        slug="orjson",
        name="orjson",
        package="orjson",
        version=version("orjson"),
    )
    format = "json"
    operations = ALL_ENCODED_OPERATIONS

    def encode_one(self, value: object) -> bytes:
        return orjson.dumps(value)

    def decode_one(self, value: bytes) -> object:
        return parent_from_primitive(cast(JsonObject, orjson.loads(value)))

    def encode_many(self, values: Sequence[object]) -> bytes:
        return orjson.dumps(values)

    def decode_many(self, value: bytes) -> list[object]:
        decoded = cast(list[JsonObject], orjson.loads(value))
        return [parent_from_primitive(item) for item in decoded]

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)


class MsgspecJsonAdapter:
    metadata = AdapterMetadata(
        slug="msgspec-json",
        name="msgspec JSON",
        package="msgspec",
        version=version("msgspec"),
    )
    format = "json"
    operations = ALL_ENCODED_OPERATIONS

    def __init__(self) -> None:
        self._encoder = msgspec.json.Encoder()
        self._one_decoder = msgspec.json.Decoder(Parent)
        self._many_decoder = msgspec.json.Decoder(list[Parent])

    def encode_one(self, value: object) -> bytes:
        return self._encoder.encode(value)

    def decode_one(self, value: bytes) -> object:
        return self._one_decoder.decode(value)

    def encode_many(self, values: Sequence[object]) -> bytes:
        return self._encoder.encode(values)

    def decode_many(self, value: bytes) -> list[object]:
        return cast(list[object], self._many_decoder.decode(value))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)


class MashumaroJsonAdapter:
    metadata = AdapterMetadata(
        slug="mashumaro-json",
        name="mashumaro JSON",
        package="mashumaro",
        version=version("mashumaro"),
    )
    format = "json"
    operations = ALL_ENCODED_OPERATIONS

    def __init__(self) -> None:
        self._one_encoder = JSONEncoder(Parent)
        self._one_decoder = JSONDecoder(Parent)
        self._many_encoder = JSONEncoder(list[Parent])
        self._many_decoder = JSONDecoder(list[Parent])

    def encode_one(self, value: object) -> bytes:
        return self._one_encoder.encode(value).encode("utf-8")

    def decode_one(self, value: bytes) -> object:
        return self._one_decoder.decode(value.decode("utf-8"))

    def encode_many(self, values: Sequence[object]) -> bytes:
        return self._many_encoder.encode(values).encode("utf-8")

    def decode_many(self, value: bytes) -> list[object]:
        return cast(list[object], self._many_decoder.decode(value.decode("utf-8")))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)


class PydanticJsonAdapter:
    metadata = AdapterMetadata(
        slug="pydantic-json",
        name="Pydantic v2 JSON",
        package="pydantic",
        version=version("pydantic"),
    )
    format = "json"
    operations = ALL_ENCODED_OPERATIONS

    def __init__(self) -> None:
        self._one = TypeAdapter(Parent)
        self._many = TypeAdapter(list[Parent])

    def encode_one(self, value: object) -> bytes:
        return self._one.dump_json(value)

    def decode_one(self, value: bytes) -> object:
        return self._one.validate_json(value)

    def encode_many(self, values: Sequence[object]) -> bytes:
        return self._many.dump_json(values)

    def decode_many(self, value: bytes) -> list[object]:
        return cast(list[object], self._many.validate_json(value))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)


class SerpycoRsJsonAdapter:
    metadata = AdapterMetadata(
        slug="serpyco-rs-json",
        name="serpyco-rs JSON",
        package="serpyco-rs",
        version=version("serpyco-rs"),
    )
    format = "json"
    operations = ALL_ENCODED_OPERATIONS

    def __init__(self) -> None:
        self._one = Serializer(Parent, codec=JSON)
        self._many = Serializer(list[Parent], codec=JSON)

    def encode_one(self, value: object) -> bytes:
        return self._one.dump(cast(Parent, value))

    def decode_one(self, value: bytes) -> object:
        return self._one.load(value)

    def encode_many(self, values: Sequence[object]) -> bytes:
        return self._many.dump(cast(list[Parent], values))

    def decode_many(self, value: bytes) -> list[object]:
        return cast(list[object], self._many.load(value))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
