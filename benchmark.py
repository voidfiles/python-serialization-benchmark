import time
from tabulate import tabulate
from contextlib import contextmanager

from subjects import (marsh, rf, serp, strain, col, hand, loli, k, lim, tmarsh, avro, pickle, serpy)
from data import ParentTestObject

SUBJECTS = (marsh, rf, serp, strain, col, hand, loli, k, lim, tmarsh, avro, pickle, serpy)

test_object = ParentTestObject()


@contextmanager
def timer(tracker):
    start = time.time()
    yield
    end = time.time()
    tracker += [end - start]


def test_many(func, limit=1000):
    for i in range(0, limit):
        subject.serialization_func([test_object, test_object], True)


def test_one(func, limit=1000):
    for i in range(0, limit):
        subject.serialization_func(test_object, False)

table = []
for subject in SUBJECTS:
    row = [subject.name]

    test_many(subject.serialization_func, 2)  # Warmup
    with timer(row):
        test_many(subject.serialization_func)

    test_one(subject.serialization_func, 2)  # Warmup
    with timer(row):
        test_one(subject.serialization_func)

    table += [row]

table = sorted(table, key=lambda x: x[1] + x[2])
relative_base = min([x[1] + x[2] for x in table])
for row in table:
    result = (row[1] + row[2]) / relative_base
    row.append(result)
print(tabulate(table, headers=['Library', 'Many Objects (seconds)', 'One Object (seconds)', 'Relative']))
