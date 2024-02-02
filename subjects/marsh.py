import marshmallow

from data import ValidatedTestObject

name = 'Marshmallow'


class SubM(marshmallow.Schema):
    w = marshmallow.fields.Int()
    x = marshmallow.fields.Method('get_x')
    y = marshmallow.fields.Str()
    z = marshmallow.fields.Int()

    def get_x(self, obj):
        return obj.x + 10


class ComplexM(marshmallow.Schema):
    bar = marshmallow.fields.Int()
    foo = marshmallow.fields.Str()
    sub = marshmallow.fields.Nested(SubM)
    subs = marshmallow.fields.Nested(SubM, many=True)


class ComplexMValidator(marshmallow.Schema):
    id = marshmallow.fields.UUID(data_key="id_")
    start_date = marshmallow.fields.Date(format="%Y-%m-%d")
    end_date = marshmallow.fields.Date(format="%Y-%m-%d")

    @marshmallow.validates_schema
    def validate_range(self, data, **kwargs) -> None:
        if data['start_date'] > data['end_date']:
            raise marshmallow.ValidationError("Start date cannot be greater than end date")

    @marshmallow.post_load
    def make_dto(self, data, **kwargs) -> ValidatedTestObject:
        return ValidatedTestObject(
            data["id"],
            data["start_date"],
            data["end_date"]
        )


schema = ComplexM()
validator = ComplexMValidator()


def serialize_func(obj, many):
    return schema.dump(obj, many=many)


def deserialize_func(obj, many):
    return validator.load(obj, many=many)
