import numpy as np

import algorithm_options


class Algorithm:
    def __init__(self):
        self.arg = []

    def options(self):
        return []


class BlindSearch(Algorithm):
    def options(self):
        return {
            'iterations': algorithm_options.IntOption(default=10, min=1, max=10000)
        }

    def run(self, space, fitness, options):
        extreme = np.inf
        for i in range(options['iterations']):
            p = space.gen_uniform_sample()
            z = fitness(p)

            if z < extreme:
                extreme = z
                self.arg = p

            yield [p]


class ClimbingSearch(Algorithm):
    def options(self):
        return {
            'iterations': algorithm_options.IntOption(default=5, min=1, max=1000),
            'population': algorithm_options.IntOption(default=10, min=1, max=1000),
            'sigma': algorithm_options.FloatOption(default=0.1, min=0.0, max=1000),
            'start_position': algorithm_options.StartPositionOption()
        }

    def run(self, space, fn, options):
        center = space.gen_uniform_sample()
        if options['start_position']:
            center = options['start_position']

        self.arg = center

        extreme = np.inf
        for i in range(options['iterations']):
            points = []
            for x in range(options['population']):
                p = center + np.random.randn(2) * options['sigma']
                z = fn(p)
                points.append(p)
                if z < extreme:
                    extreme = z
                    self.arg = p

            center = self.arg
            yield points


class Anneling(Algorithm):
    def options(self):
        return {
            'initial_temp': algorithm_options.IntOption(default=2000, min=10, max=100000),
            'final_temp': algorithm_options.IntOption(default=50, min=10, max=100000),
            'alpha': algorithm_options.FloatOption(default=0.99),
            'sigma': algorithm_options.FloatOption(default=0.1, min=0.0, max=1000),
            'start_position': algorithm_options.StartPositionOption()
        }

    def run(self, space, fn, options):
        x0 = space.gen_uniform_sample()
        if options['start_position']:
            x0 = np.array(options['start_position'])

        T = options['initial_temp']
        while T > options['final_temp']:
            x = x0 + np.random.randn(2) * options['sigma']
            delta = fn(x) - fn(x0)

            # take better solution
            if delta > 0:
                x0 = x
            else:
                r = np.random.uniform(0, 1)
                if r < np.exp(-delta/T):
                    x0 = x

            yield [x0]

            # reduce temperature
            T *= options['alpha']

        self.arg = x0









class GridAlgorithm(Algorithm):
    def options(self):
        return [
            {'name': 'num', 'default': 10, 'transform': int}
        ]

    def run(self, space, fn, options):
        self.arg = []
        extreme = 0
        points = []
        for x in np.linspace(space.sizes[0][0], space.sizes[0][1], options['num']):
            for y in np.linspace(space.sizes[1][0], space.sizes[1][1], options['num']):
                points.append((x, y, fn(np.array([x, y]))))

        yield points

