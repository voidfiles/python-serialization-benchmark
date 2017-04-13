import lima

__name__ = 'lima'


class SubM(lima.Schema):
    w = lima.fields.Integer()
    x = lima.fields.Integer(get=lambda obj: obj.x + 10)
    y = lima.fields.Integer()
    z = lima.fields.Integer()


class ComplexM(lima.Schema):
    foo = lima.fields.String()
    bar = lima.fields.Integer(get=lambda obj: obj.bar())
    sub = lima.fields.Embed(schema=SubM)
    subs = lima.fields.Embed(schema=SubM, many=True)


schema = ComplexM()
many_scheam = ComplexM(many=True)


def serialization_func(obj, many):
    if many:
        return many_scheam.dump(obj)
    else:
        return schema.dump(obj)
