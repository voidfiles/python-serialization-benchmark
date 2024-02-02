from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4


class ChildTestObject:
    def __init__(self, multiplier=None):
        self.w = 1000 * multiplier if multiplier else 100
        self.x = 20 * multiplier if multiplier else 20
        self.y = 'hello' * multiplier if multiplier else 'hello'
        self.z = 10 * multiplier if multiplier else 10


class ParentTestObject:
    def __init__(self, my_validated_field=None):
        self.foo = 'bar'
        self.sub = ChildTestObject()
        self.subs = [ChildTestObject(i) for i in range(10)]
        self.my_validated_field = my_validated_field

    @property
    def bar(self):
        return 5


@dataclass
class ValidatedTestObject:
    id_: UUID
    start_date: date
    end_date: date


data_to_validate = {"id_": uuid4(), "start_date": "2023-12-12", "end_date": "2023-12-13"}
