import random
import types
from timeit import default_timer as timer

import numpy as np

import test_functions
import algorithms


class Space:
    def __init__(self, sizes):
        self.sizes = sizes

    def gen_uniform_sample(self):
        return np.array([random.uniform(s[0], s[1]) for s in self.sizes])

    def in_range(self, p):
        for value, constraint in zip(p, self.sizes):
            if value < constraint[0] or value > constraint[1]:
                return False

        return True

    def gen_in_range(self, cb):
        for i in range(100):
            val = cb()
            if self.in_range(val):
                return val
        return None



class MeasureContext:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = timer()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(self.name, timer() - self.start)


class CountCallsProxy:
    def __init__(self, fn):
        self.fn = fn
        self.called_count = 0

    def __call__(self, *args, **kwargs):
        self.called_count += 1
        return self.fn(*args, **kwargs)


def all_functions():
    return [getattr(test_functions, fn) for fn in dir(test_functions) if isinstance(getattr(test_functions, fn), types.FunctionType)]


def all_algorithms():
    return [
        algorithms.Soma,
        algorithms.BlindSearch,
        algorithms.ClimbingSearch,
        algorithms.Anneling
    ]