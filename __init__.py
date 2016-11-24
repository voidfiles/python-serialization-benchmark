import serpy


class SubS(serpy.Serializer):
    w = serpy.IntField()
    x = serpy.MethodField()
    y = serpy.StrField()
    z = serpy.IntField()

    def get_x(self, obj):
        return obj.x + 10


class ComplexS(serpy.Serializer):
    foo = serpy.StrField()
    bar = serpy.IntField(call=True)
    sub = SubS()
    subs = SubS(many=True)


def serializaion_func(obj, many):
    return ComplexS(obj, many=many).data
