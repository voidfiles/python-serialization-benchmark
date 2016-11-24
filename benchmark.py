import time
from tabulate import tabulate
from contextlib import contextmanager

from subjects import (marsh, rf, serp, strain, col)
from data import ParentTestObject

SUBJECTS = (marsh, rf, serp, strain, col)

test_object = ParentTestObject()


@contextmanager
def timer(tracker):
    start = time.time()
    yield
    end = time.time()
    tracker += [end - start]


def test_many(func, limit=100):
    for i in xrange(0, limit):
        subject.serialization_func([test_object, test_object], True)


def test_one(func, limit=1000):
    for i in xrange(0, limit):
        subject.serialization_func(test_object, False)

table = []
for subject in SUBJECTS:
    row = [subject.__name__]

    with timer(row):
        test_one(subject.serialization_func)

    with timer(row):
        test_many(subject.serialization_func)

    table += [row]

table = sorted(table, key=lambda x: x[1] + x[2])
print tabulate(table, headers=['Library', 'One Object', 'Many Objects'])
