import pickle

name = 'Pickle'


def serialization_func(obj, many):
    return pickle.dumps(obj)
