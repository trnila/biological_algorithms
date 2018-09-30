import numpy as np
from PyQt5.QtWidgets import QDoubleSpinBox


class BlindSearch:
    def options(self):
        return [
            {'name': 'iterations', 'transform': int, 'default': 10}
        ]

    def run(self, space, fitness, options):
        self.min = np.inf
        for i in range(options['iterations']):
            p = space.gen_uniform_sample()
            z = fitness(p)

            if z < self.min:
                self.min = z
                self.arg = p

            yield [(p[0], p[1], z)]


class ClimbingSearch:
    def options(self):
        return [
            {'name': 'iterations', 'transform': int, 'default': 5},
            {'name': 'population', 'transform': int, 'default': 5},
            {'name': 'sigma', 'transform': float, 'default': 0.1, 'type': QDoubleSpinBox},
        ]

    def run(self, space, fn, options):
        self.arg = space.gen_uniform_sample()
        self.min = np.inf
        for i in range(options['iterations']):
            points = []
            for x in range(options['population']):
                p = self.arg + np.random.randn(2) * options['sigma']
                z = fn(p)
                points.append((p[0], p[1], z))
                if z < self.min:
                    self.min = z
                    self.arg = p
            yield points