import marshmallow

__name__ = 'Marshmallow'


class SubM(marshmallow.Schema):
    w = marshmallow.fields.Int()
    x = marshmallow.fields.Method('get_x')
    y = marshmallow.fields.Str()
    z = marshmallow.fields.Int()

    def get_x(self, obj):
        return obj.x + 10


class ComplexM(marshmallow.Schema):
    foo = marshmallow.fields.Str()
    bar = marshmallow.fields.Int()
    sub = marshmallow.fields.Nested(SubM)
    subs = marshmallow.fields.Nested(SubM, many=True)


schema = ComplexM()


def serialization_func(obj, many):
    return schema.dump(obj, many=many).data
