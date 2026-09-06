import pytest

from serialization_benchmark.adapters.baselines import HandwrittenAdapter
from serialization_benchmark.contracts import AdapterMetadata, JsonObject
from serialization_benchmark.fixtures import make_fixtures
from serialization_benchmark.validation import (
    AdapterValidationError,
    validate_primitive_adapter,
)


class BrokenAdapter(HandwrittenAdapter):
    metadata = AdapterMetadata(
        slug="broken",
        name="Broken",
        package="test",
        version="1",
    )

    def dump_one(self, value: object) -> JsonObject:
        return {"wrong": True}


def test_validation_names_the_broken_operation() -> None:
    with pytest.raises(AdapterValidationError, match="broken.dump_one"):
        validate_primitive_adapter(BrokenAdapter(), make_fixtures())
