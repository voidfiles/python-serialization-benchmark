import pickle

__name__ = 'Pickle'


def serialization_func(obj, many):
    return pickle.dumps(obj)
