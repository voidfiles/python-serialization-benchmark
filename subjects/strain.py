import strainer

__name__ = 'Strainer'

sub_strainer_serializer = strainer.serializer(
  strainer.field('w'),
  strainer.field('x', attr_getter=lambda obj: obj.x + 10),
  strainer.field('y'),
  strainer.field('z'),
)

complex_strainer_serializer = strainer.serializer(
  strainer.field('foo'),
  strainer.field('bar', attr_getter=lambda obj: obj.bar()),
  strainer.child('sub', serializer=sub_strainer_serializer),
  strainer.many('subs', serializer=sub_strainer_serializer),
)


def serialization_func(obj, many):
    if many:
        return [complex_strainer_serializer.serialize(x) for x in obj]
    else:
        return complex_strainer_serializer.serialize(obj)
