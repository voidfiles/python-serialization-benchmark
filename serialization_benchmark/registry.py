from serialization_benchmark.adapters.baselines import (
    DataclassesAsdictAdapter,
    HandwrittenAdapter,
)
from serialization_benchmark.adapters.adaptix import AdaptixAdapter
from serialization_benchmark.adapters.cattrs import CattrsAdapter
from serialization_benchmark.adapters.drf import DrfAdapter
from serialization_benchmark.adapters.encoded_json import (
    MashumaroJsonAdapter,
    MsgspecJsonAdapter,
    OrjsonAdapter,
    PydanticJsonAdapter,
    SerpycoRsJsonAdapter,
    StdlibJsonAdapter,
)
from serialization_benchmark.adapters.encoded_msgpack import (
    MashumaroMessagePackAdapter,
    MsgspecMessagePackAdapter,
    OrmsgpackAdapter,
    SerpycoRsMessagePackAdapter,
)
from serialization_benchmark.adapters.marshmallow import MarshmallowAdapter
from serialization_benchmark.adapters.mashumaro import MashumaroAdapter
from serialization_benchmark.adapters.msgspec import MsgspecAdapter
from serialization_benchmark.adapters.pydantic import PydanticAdapter
from serialization_benchmark.adapters.serpyco_rs import SerpycoRsAdapter
from serialization_benchmark.contracts import EncodedAdapter, PrimitiveAdapter

_PRIMITIVE_ADAPTERS: tuple[PrimitiveAdapter, ...] = (
    HandwrittenAdapter(),
    DataclassesAsdictAdapter(),
    MarshmallowAdapter(),
    DrfAdapter(),
    CattrsAdapter(),
    MashumaroAdapter(),
    MsgspecAdapter(),
    PydanticAdapter(),
    SerpycoRsAdapter(),
    AdaptixAdapter(),
)
_ENCODED_ADAPTERS: tuple[EncodedAdapter, ...] = (
    StdlibJsonAdapter(),
    OrjsonAdapter(),
    MsgspecJsonAdapter(),
    MashumaroJsonAdapter(),
    PydanticJsonAdapter(),
    SerpycoRsJsonAdapter(),
    MsgspecMessagePackAdapter(),
    MashumaroMessagePackAdapter(),
    SerpycoRsMessagePackAdapter(),
    OrmsgpackAdapter(),
)


def primitive_adapters() -> tuple[PrimitiveAdapter, ...]:
    return _PRIMITIVE_ADAPTERS


def encoded_adapters() -> tuple[EncodedAdapter, ...]:
    return _ENCODED_ADAPTERS
