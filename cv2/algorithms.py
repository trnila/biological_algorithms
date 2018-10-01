import numpy as np
from PyQt5.QtWidgets import QDoubleSpinBox

class Algorithm:
    def __init__(self):
        self.min = 0
        self.arg = []

    def options(self):
        return []


class BlindSearch(Algorithm):
    def options(self):
        return [
            {'name': 'iterations', 'transform': int, 'default': 10}
        ]

    def run(self, space, fitness, options):
        self.min = np.inf
        for i in range(options['iterations']):
            p = space.gen_uniform_sample()
            z = fitness(p)

            if options['comparator'](z, self.min):
                self.min = z
                self.arg = p

            yield [(p[0], p[1], z)]


class ClimbingSearch(Algorithm):
    def options(self):
        return [
            {'name': 'iterations', 'transform': int, 'default': 5},
            {'name': 'population', 'transform': int, 'default': 50},
            {'name': 'sigma', 'transform': float, 'default': 0.1, 'type': 'double'},
            {'name': 'start_position', 'type': 'position', 'transform': lambda x: x}
        ]

    def run(self, space, fn, options):
        self.arg = space.gen_uniform_sample()

        if options['start_position']:
            self.arg = options['start_position']


        self.min = np.inf
        for i in range(options['iterations']):
            points = []
            for x in range(options['population']):
                p = self.arg + np.random.randn(2) * options['sigma']
                z = fn(p)
                points.append((p[0], p[1], z))
                if options['comparator'](z, self.min):
                    self.min = z
                    self.arg = p
            yield points


class GridAlgorithm(Algorithm):
    def options(self):
        return [
            {'name': 'num', 'default': 10, 'transform': int}
        ]

    def run(self, space, fn, options):
        self.arg = []
        self.min = 0
        points = []
        for x in np.linspace(space.sizes[0][0], space.sizes[0][1], options['num']):
            for y in np.linspace(space.sizes[1][0], space.sizes[1][1], options['num']):
                points.append((x, y, fn(np.array([x, y]))))

        yield points

