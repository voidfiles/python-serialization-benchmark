import dataclasses
import typing

import serpyco

from data import ParentTestObject

name = "serpyco"


def get_x(obj):
    return obj.x + 10


@dataclasses.dataclass
class SubM:
    w: int
    y: str
    z: int
    x: int = serpyco.field(getter=get_x)


@dataclasses.dataclass
class ComplexM:
    foo: str
    sub: SubM
    subs: typing.List[SubM]
    bar: int = serpyco.field(getter=ParentTestObject.bar)


serializer = serpyco.Serializer(ComplexM)


def serialization_func(obj, many):
    return serializer.dump(obj, many=many)
