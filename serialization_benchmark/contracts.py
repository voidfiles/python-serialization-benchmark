from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol, Sequence

if TYPE_CHECKING:
    from serialization_benchmark.fixtures import Parent

type JsonScalar = None | bool | int | float | str
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]
type PrimitiveOperation = Literal["dump_one", "load_one", "dump_many", "load_many"]
type EncodedOperation = Literal["encode_one", "decode_one", "encode_many", "decode_many"]
type EncodedFormat = Literal["json", "messagepack", "avro", "pickle"]
type ModelStrategy = Literal["dataclass"]

ALL_PRIMITIVE_OPERATIONS: frozenset[PrimitiveOperation] = frozenset(
    {"dump_one", "load_one", "dump_many", "load_many"}
)
ALL_ENCODED_OPERATIONS: frozenset[EncodedOperation] = frozenset(
    {"encode_one", "decode_one", "encode_many", "decode_many"}
)
ALL_ENCODED_FORMATS: frozenset[EncodedFormat] = frozenset(
    {"json", "messagepack", "avro", "pickle"}
)


@dataclass(frozen=True)
class AdapterMetadata:
    slug: str
    name: str
    package: str
    version: str
    model_strategy: ModelStrategy = "dataclass"
    prerelease: bool = False


class PrimitiveAdapter(Protocol):
    metadata: AdapterMetadata
    operations: frozenset[PrimitiveOperation]

    def dump_one(self, value: object) -> JsonObject: ...
    def load_one(self, value: JsonObject) -> object: ...
    def dump_many(self, values: Sequence[object]) -> list[JsonObject]: ...
    def load_many(self, values: Sequence[JsonObject]) -> list[object]: ...
    def normalize(self, value: object) -> Parent: ...


class EncodedAdapter(Protocol):
    metadata: AdapterMetadata
    format: EncodedFormat
    operations: frozenset[EncodedOperation]

    def encode_one(self, value: object) -> bytes: ...
    def decode_one(self, value: bytes) -> object: ...
    def encode_many(self, values: Sequence[object]) -> bytes: ...
    def decode_many(self, value: bytes) -> list[object]: ...
    def normalize(self, value: object) -> Parent: ...
