import colander

__name__ = 'Colander'


class Sub(colander.MappingSchema):
    w = colander.SchemaNode(colander.Int())
    y = colander.SchemaNode(colander.String())
    x = colander.SchemaNode(colander.Int())
    z = colander.SchemaNode(colander.Int())


class Subs(colander.SequenceSchema):
    phone = Sub()


class Parent(colander.MappingSchema):
    foo = colander.SchemaNode(colander.String())
    bar = colander.SchemaNode(colander.Int())
    sub = Sub()
    subs = Subs()

schema = Parent()


def sub_to_cstruct(obj):
    return {
        'w': obj.w,
        'y': obj.y,
        'x': obj.x + 10,
        'z': obj.z
    }


def obj_to_cstruct(obj):
    return {
      'foo': obj.foo,
      'bar': obj.bar(),
      'sub': sub_to_cstruct(obj.sub),
      'subs': [sub_to_cstruct(x) for x in obj.subs],
    }


def serialization_func(obj, many):
    if many:
        return [schema.deserialize(obj_to_cstruct(x)) for x in obj]
    else:
        return schema.deserialize(obj_to_cstruct(obj))
