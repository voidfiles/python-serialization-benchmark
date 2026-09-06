from __future__ import annotations

import pickle
import platform
from typing import Sequence

from serialization_benchmark.contracts import ALL_ENCODED_OPERATIONS, AdapterMetadata
from serialization_benchmark.fixtures import Parent, normalize_parent


class PickleAdapter:
    metadata = AdapterMetadata(
        slug="pickle",
        name="pickle",
        package="python",
        version=platform.python_version(),
    )
    format = "pickle"
    operations = ALL_ENCODED_OPERATIONS

    def encode_one(self, value: object) -> bytes:
        return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

    def decode_one(self, value: bytes) -> object:
        return pickle.loads(value)

    def encode_many(self, values: Sequence[object]) -> bytes:
        return pickle.dumps(values, protocol=pickle.HIGHEST_PROTOCOL)

    def decode_many(self, value: bytes) -> list[object]:
        decoded = pickle.loads(value)
        if not isinstance(decoded, list):
            raise TypeError(f"expected list, got {type(decoded).__name__}")
        return decoded

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
