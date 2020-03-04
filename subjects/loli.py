from collections import namedtuple
from lollipop.types import Object, String, Integer, List, FunctionField, MethodField

name = 'Lollipop'

SubS = namedtuple('SubS', ['w', 'x', 'y', 'z'])
ComplexS = namedtuple('ComplexS', ['foo', 'bar', 'sub', 'subs'])


def get_x(obj):
    return obj.x + 10


SubSType = Object({
    'w': Integer(),
    'x': FunctionField(Integer(), get_x),
    'y': String(),
    'z': Integer(),
}, constructor=SubS)

ComplexSType = Object({
    'foo': String(),
    'bar': MethodField(Integer(), 'bar'),
    'sub': SubSType,
    'subs': List(SubSType),
}, constructor=ComplexS)


def serialization_func(obj, many):
    if many:
        return List(ComplexSType).dump(obj)
    else:
        return ComplexSType.dump(obj)
