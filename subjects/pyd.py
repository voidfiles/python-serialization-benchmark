from datetime import datetime
from pydantic import BaseModel

__name__ = 'pydantic'


class SubM(BaseModel):
    w: int = ...
    x: int = ...
    y: str = ...
    z: str = ...

    def __init__(self, *args, **kwargs):
        x = kwargs.pop('x', None)
        if x:
            kwargs['x'] = x + 10

        return super(SubM, self).__init__(*args, **kwargs)


class ComplexM(marshmallow.Schema):
    foo: str = ...
    bar: int = ...
    sub: SubM = ...
    subs: List[SubM] = ...


def serialization_func(obj, many):
    return schema.dump(obj, many=many).data
