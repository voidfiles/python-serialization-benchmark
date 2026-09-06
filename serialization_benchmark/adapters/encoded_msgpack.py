from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

import msgspec
import ormsgpack
from mashumaro.codecs.msgpack import MessagePackDecoder, MessagePackEncoder
from serpyco_rs import MSGPACK, Serializer

from serialization_benchmark.contracts import (
    ALL_ENCODED_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import (
    Parent,
    normalize_parent,
    parent_from_primitive,
)


class MsgspecMessagePackAdapter:
    metadata = AdapterMetadata(
        slug="msgspec-msgpack",
        name="msgspec MessagePack",
        package="msgspec",
        version=version("msgspec"),
    )
    format = "messagepack"
    operations = ALL_ENCODED_OPERATIONS

    def __init__(self) -> None:
        self._encoder = msgspec.msgpack.Encoder()
        self._one_decoder = msgspec.msgpack.Decoder(Parent)
        self._many_decoder = msgspec.msgpack.Decoder(list[Parent])

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


class MashumaroMessagePackAdapter:
    metadata = AdapterMetadata(
        slug="mashumaro-msgpack",
        name="mashumaro MessagePack",
        package="mashumaro",
        version=version("mashumaro"),
    )
    format = "messagepack"
    operations = ALL_ENCODED_OPERATIONS

    def __init__(self) -> None:
        self._one_encoder = MessagePackEncoder(Parent)
        self._one_decoder = MessagePackDecoder(Parent)
        self._many_encoder = MessagePackEncoder(list[Parent])
        self._many_decoder = MessagePackDecoder(list[Parent])

    def encode_one(self, value: object) -> bytes:
        return self._one_encoder.encode(value)

    def decode_one(self, value: bytes) -> object:
        return self._one_decoder.decode(value)

    def encode_many(self, values: Sequence[object]) -> bytes:
        return self._many_encoder.encode(values)

    def decode_many(self, value: bytes) -> list[object]:
        return cast(list[object], self._many_decoder.decode(value))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)


class SerpycoRsMessagePackAdapter:
    metadata = AdapterMetadata(
        slug="serpyco-rs-msgpack",
        name="serpyco-rs MessagePack",
        package="serpyco-rs",
        version=version("serpyco-rs"),
    )
    format = "messagepack"
    operations = ALL_ENCODED_OPERATIONS

    def __init__(self) -> None:
        self._one = Serializer(Parent, codec=MSGPACK)
        self._many = Serializer(list[Parent], codec=MSGPACK)

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


class OrmsgpackAdapter:
    metadata = AdapterMetadata(
        slug="ormsgpack",
        name="ormsgpack",
        package="ormsgpack",
        version=version("ormsgpack"),
    )
    format = "messagepack"
    operations = ALL_ENCODED_OPERATIONS

    def encode_one(self, value: object) -> bytes:
        return ormsgpack.packb(value)

    def decode_one(self, value: bytes) -> object:
        return parent_from_primitive(cast(JsonObject, ormsgpack.unpackb(value)))

    def encode_many(self, values: Sequence[object]) -> bytes:
        return ormsgpack.packb(values)

    def decode_many(self, value: bytes) -> list[object]:
        raw = cast(list[JsonObject], ormsgpack.unpackb(value))
        return [parent_from_primitive(item) for item in raw]

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
