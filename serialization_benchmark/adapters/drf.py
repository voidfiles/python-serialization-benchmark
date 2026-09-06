from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

from rest_framework import serializers

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import Child, Parent, normalize_parent


class ChildSerializer(serializers.Serializer):
    w = serializers.IntegerField()
    x = serializers.IntegerField()
    y = serializers.CharField()
    z = serializers.IntegerField()


class ParentSerializer(serializers.Serializer):
    foo = serializers.CharField()
    count = serializers.IntegerField()
    active = serializers.BooleanField()
    ratio = serializers.FloatField()
    sub = ChildSerializer()
    subs = ChildSerializer(many=True)

    def create(self, validated_data: dict[str, object]) -> Parent:
        raw_sub = cast(dict[str, object], validated_data["sub"])
        raw_subs = cast(list[dict[str, object]], validated_data["subs"])

        def make_child(item: dict[str, object]) -> Child:
            return Child(
                w=int(item["w"]),
                x=int(item["x"]),
                y=str(item["y"]),
                z=int(item["z"]),
            )

        return Parent(
            foo=str(validated_data["foo"]),
            count=int(validated_data["count"]),
            active=bool(validated_data["active"]),
            ratio=float(validated_data["ratio"]),
            sub=make_child(raw_sub),
            subs=[make_child(item) for item in raw_subs],
        )


class DrfAdapter:
    metadata = AdapterMetadata(
        slug="drf",
        name="Django REST Framework",
        package="djangorestframework",
        version=version("djangorestframework"),
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def __init__(self) -> None:
        self._one = ParentSerializer()
        self._many = ParentSerializer(many=True)

    def load_one(self, value: JsonObject) -> object:
        validated_data = cast(dict[str, object], self._one.run_validation(value))
        return self._one.create(validated_data)

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        validated_data = cast(
            list[dict[str, object]], self._many.run_validation(values)
        )
        return cast(list[object], self._many.create(validated_data))

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, self._one.to_representation(value))

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return cast(list[JsonObject], self._many.to_representation(values))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
