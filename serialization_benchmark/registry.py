from serialization_benchmark.adapters.baselines import (
    DataclassesAsdictAdapter,
    HandwrittenAdapter,
)
from serialization_benchmark.adapters.marshmallow import MarshmallowAdapter
from serialization_benchmark.contracts import EncodedAdapter, PrimitiveAdapter

_PRIMITIVE_ADAPTERS: tuple[PrimitiveAdapter, ...] = (
    HandwrittenAdapter(),
    DataclassesAsdictAdapter(),
    MarshmallowAdapter(),
)
_ENCODED_ADAPTERS: tuple[EncodedAdapter, ...] = ()


def primitive_adapters() -> tuple[PrimitiveAdapter, ...]:
    return _PRIMITIVE_ADAPTERS


def encoded_adapters() -> tuple[EncodedAdapter, ...]:
    return _ENCODED_ADAPTERS
