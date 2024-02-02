import time
from tabulate import tabulate
from contextlib import contextmanager

from subjects import (marsh, rf, dantic)
from data import ParentTestObject, data_to_validate


@contextmanager
def timer(tracker):
    start = time.time()
    yield
    end = time.time()
    tracker += [end - start]


def test_many(func, test_object, limit=1000):
    for i in range(0, limit):
        func([test_object]*2, many=True)


def test_one(func, test_object, limit=1000):
    for i in range(0, limit):
        func(test_object, many=False)


def benchmark(type_="serialize"):
    SUBJECTS = (marsh, rf, dantic)

    test_objects = {
        "serialize": (ParentTestObject(), "serialize_func"),
        "deserialize": (data_to_validate, "deserialize_func"),
    }

    table = []
    REPETITIONS = 1000
    for subject in SUBJECTS:
        row = [subject.name]
        test_obj, test_func = test_objects[type_]
        func = getattr(subject, test_func)

        test_many(func, test_obj, 2)  # Warmup
        with timer(row):
            test_many(func, test_obj, REPETITIONS)

        test_one(func, test_obj, 2)  # Warmup
        with timer(row):
            test_one(func, test_obj, REPETITIONS)

        table += [row]

    table = sorted(table, key=lambda x: x[1] + x[2])
    relative_base = min([x[1] + x[2] for x in table])
    # print(table, relative_base)
    for row in table:
        result = (row[1] + row[2]) / relative_base
        row.append(result)

    print(type_)
    print(tabulate(table, headers=['Library', f'Many Objects {REPETITIONS} times (seconds)', f'One Object {REPETITIONS} times (seconds)', 'Relative']))


if __name__ == "__main__":
    benchmark("serialize")
    print("=============\n\n")
    benchmark("deserialize")
