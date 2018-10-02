import numpy as np

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
        center = space.gen_uniform_sample()
        if options['start_position']:
            center = options['start_position']

        self.arg = center

        self.min = np.inf
        for i in range(options['iterations']):
            points = []
            for x in range(options['population']):
                p = center + np.random.randn(2) * options['sigma']
                z = fn(p)
                points.append((*p, z))
                if options['comparator'](z, self.min):
                    self.min = z
                    self.arg = p

            center = self.arg
            yield points


class Anneling(Algorithm):
    def options(self):
        return [
            {'name': 'initial_temp', 'transform': float, 'default': 2000, 'type': 'double'},
            {'name': 'final_temp', 'transform': float, 'default': 50, 'type': 'double'},
            {'name': 'cycles', 'transform': int, 'default': 100},
            {'name': 'alpha', 'default': 0.99, 'transform': float, 'type': 'double'}
        ]

    def run(self, space, fn, options):
        x0 = space.gen_uniform_sample()
        T = options['initial_temp']
        while T > options['final_temp']:
            x = x0 + np.random.randn(2) #0.5
            delta = fn(x) - fn(x0)

            # take better solution
            if delta > 0:
                x0 = x
            else:
                r = np.random.uniform(0, 1)
                if r < np.exp(-delta/T):
                    x0 = x

            yield [(*x0, fn(x0))]

            # reduce temperature
            #T *= options['alpha']
            T *= 0.99









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

