import pytest

from serialization_benchmark.contracts import PrimitiveAdapter
from serialization_benchmark.fixtures import make_fixtures
from serialization_benchmark.registry import primitive_adapters
from serialization_benchmark.validation import validate_primitive_adapter


@pytest.mark.parametrize(
    "adapter",
    primitive_adapters(),
    ids=lambda adapter: adapter.metadata.slug,
)
def test_registered_primitive_adapter_is_semantically_correct(
    adapter: PrimitiveAdapter,
) -> None:
    validate_primitive_adapter(adapter, make_fixtures())
