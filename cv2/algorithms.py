import numpy as np
from PyQt5.QtWidgets import QDoubleSpinBox


class BlindSearch:
    def options(self):
        return [
            {'name': 'iterations', 'transform': int, 'default': 10}
        ]

    def run(self, space, fitness, options):
        for i in range(options['iterations']):
            p = space.gen_uniform_sample()
            z = fitness(p)
            yield [(p[0], p[1], z)]


class ClimbingSearch:
    def options(self):
        return [
            {'name': 'iterations', 'transform': int, 'default': 5},
            {'name': 'population', 'transform': int, 'default': 5},
            {'name': 'sigma', 'transform': float, 'default': 0.1, 'type': QDoubleSpinBox},
        ]

    def run(self, space, fn, options):
        start = space.gen_uniform_sample()
        for i in range(options['iterations']):
            m = np.Infinity
            arg = None
            points = []
            for x in range(options['population']):
                p = start + np.random.randn(2) * options['sigma']
                z = fn(p)
                points.append((p[0], p[1], z))
                if z < m:
                    m = z
                    arg = p
            yield points
            start = arg