from datetime import date
from uuid import UUID

import pydantic
from pydantic import Field, computed_field

name = "Pydantic"


class SubP(pydantic.BaseModel):
    w: int
    x_: int
    y: str
    z: int

    @computed_field
    @property
    def x(self) -> int:
        return self.x_ + 10


class ComplexP(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    bar: int
    foo: str
    sub: SubP
    subs: list[SubP]


class ComplexPValidator(pydantic.BaseModel):
    id: UUID = Field(alias="id_")
    start_date: date
    end_date: date


def serialize_func(obj, many):
    if many:
        return [
            ComplexP(
                bar=o.bar,
                foo=o.foo,
                sub=SubP(w=o.sub.w, x_=o.sub.x, y=o.sub.y, z=o.sub.z),
                subs=[SubP(w=s.w, x_=s.x, y=s.y, z=s.z) for s in o.subs]
            ).model_dump()
            for o in obj
        ]
    serializer = ComplexP(
        bar=obj.bar,
        foo=obj.foo,
        sub=SubP(w=obj.sub.w, x_=obj.sub.x, y=obj.sub.y, z=obj.sub.z),
        subs=[SubP(w=s.w, x_=s.x, y=s.y, z=s.z) for s in obj.subs]
    )
    return serializer.model_dump()


def deserialize_func(obj, many):
    if many:
        return [ComplexPValidator(**o) for o in obj]
    return ComplexPValidator(**obj)
