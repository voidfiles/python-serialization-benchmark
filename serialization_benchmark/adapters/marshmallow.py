from __future__ import annotations

from importlib.metadata import version
from typing import Sequence, cast

from marshmallow import Schema, fields, post_load

from serialization_benchmark.contracts import (
    ALL_PRIMITIVE_OPERATIONS,
    AdapterMetadata,
    JsonObject,
)
from serialization_benchmark.fixtures import Child, Parent, normalize_parent


class ChildSchema(Schema):
    w = fields.Integer(required=True)
    x = fields.Integer(required=True)
    y = fields.String(required=True)
    z = fields.Integer(required=True)

    @post_load
    def make_child(self, data: dict[str, object], **_: object) -> Child:
        return Child(
            w=int(data["w"]),
            x=int(data["x"]),
            y=str(data["y"]),
            z=int(data["z"]),
        )


class ParentSchema(Schema):
    foo = fields.String(required=True)
    count = fields.Integer(required=True)
    active = fields.Boolean(required=True)
    ratio = fields.Float(required=True)
    sub = fields.Nested(ChildSchema(), required=True)
    subs = fields.List(fields.Nested(ChildSchema()), required=True)

    @post_load
    def make_parent(self, data: dict[str, object], **_: object) -> Parent:
        sub = data["sub"]
        subs = data["subs"]
        if not isinstance(sub, Child) or not isinstance(subs, list):
            raise TypeError("marshmallow returned invalid nested values")
        if not all(isinstance(child, Child) for child in subs):
            raise TypeError("marshmallow returned an invalid child list")
        return Parent(
            foo=str(data["foo"]),
            count=int(data["count"]),
            active=bool(data["active"]),
            ratio=float(data["ratio"]),
            sub=sub,
            subs=subs,
        )


class MarshmallowAdapter:
    metadata = AdapterMetadata(
        slug="marshmallow",
        name="Marshmallow",
        package="marshmallow",
        version=version("marshmallow"),
    )
    operations = ALL_PRIMITIVE_OPERATIONS

    def __init__(self) -> None:
        self._one = ParentSchema()
        self._many = ParentSchema(many=True)

    def dump_one(self, value: object) -> JsonObject:
        return cast(JsonObject, self._one.dump(value))

    def load_one(self, value: JsonObject) -> object:
        return self._one.load(value)

    def dump_many(self, values: Sequence[object]) -> list[JsonObject]:
        return cast(list[JsonObject], self._many.dump(values))

    def load_many(self, values: Sequence[JsonObject]) -> list[object]:
        return cast(list[object], self._many.load(values))

    def normalize(self, value: object) -> Parent:
        return normalize_parent(value)
