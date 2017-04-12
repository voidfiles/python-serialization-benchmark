from kim import Mapper, field

__name__ = 'kim'


class Complex(object):
    pass


class SubResource(object):
    pass


def bar_pipe(session):
    session.output['bar'] = session.data()


def x_pipe(session):
    session.output['x'] = session.data + 10


class SubMapper(Mapper):
        __type__ = SubResource
        w = field.String()
        x = field.String(extra_serialize_pipes={'output': [x_pipe]})
        y = field.String()
        z = field.String()


class ComplexMapper(Mapper):
        __type__ = Complex
        foo = field.String()
        bar = field.String(extra_serialize_pipes={'output': [bar_pipe]})
        sub = field.Nested(SubMapper)
        subs = field.Collection(field.Nested(SubMapper))


def serialization_func(obj, many):
    if many:
        return ComplexMapper.many().serialize(obj)
    else:
        return ComplexMapper(obj=obj).serialize()
