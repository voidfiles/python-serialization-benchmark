name = 'Custom'


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
        return [obj_to_cstruct(x) for x in obj]
    else:
        return obj_to_cstruct(obj)
