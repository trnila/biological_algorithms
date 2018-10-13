import math

import numpy as np
import collections

import algorithm_options


class Algorithm:
    def __init__(self):
        self.arg = []

    def options(self):
        return []


class BlindSearch(Algorithm):
    def options(self):
        return {
            'iterations': algorithm_options.IntOption(default=2000, min=1, max=10000)
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
            'iterations': algorithm_options.IntOption(default=100, min=1, max=1000),
            'population': algorithm_options.IntOption(default=20, min=1, max=1000),
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
            'initial_temp': algorithm_options.FloatOption(default=2000, min=10, max=100000),
            'final_temp': algorithm_options.FloatOption(default=0.00000375, min=0.0000000001, max=100000),
            'alpha': algorithm_options.FloatOption(default=0.99),
            'sigma': algorithm_options.FloatOption(default=0.1, min=0.0, max=1000),
            'start_position': algorithm_options.StartPositionOption()
        }

    def run(self, space, fn, options):
        x0 = space.gen_uniform_sample()
        if options['start_position']:
            x0 = np.array(options['start_position'])

        prev_val = np.inf
        T = options['initial_temp']
        while T > options['final_temp']:
            x = x0 + np.random.randn(2) * options['sigma']
            z = fn(x)

            # take better solution
            if z < prev_val:
                x0 = x
                prev_val = z
            else:
                r = np.random.uniform(0, 1)
                if r < np.exp(-(z - prev_val)/T):
                    x0 = x
                    prev_val = z

            yield [x0]

            # reduce temperature
            T *= options['alpha']

        self.arg = x0


Unit = collections.namedtuple('Unit', ['arg', 'cost'])

class Soma(Algorithm):
    def options(self):
        return {
            'path_length': algorithm_options.FloatOption(default=3.0, min=0.1, max=100000),
            'step_size': algorithm_options.FloatOption(default=0.11, min=0.0000000001, max=100000),
            'pop_size': algorithm_options.IntOption(default=10, min=2, max=100000),
            'prt': algorithm_options.FloatOption(default=0.1),
            'migrations': algorithm_options.IntOption(default=10, min=2, max=100000),
        }

    def transform(self, values):
        return [value.arg for value in values]

    def run(self, space, fn, options):
        points = [space.gen_uniform_sample() for _ in range(options['pop_size'])]
        population = [Unit(arg=pos, cost=fn(pos)) for pos in points]

        yield self.transform(population)

        for i in range(options['migrations']):
            leader = self.find_leader(population)

            new_population = []
            for obj in population:
                best_pos = None
                best_value = np.inf
                t = options['step_size']

                diff = leader.arg - obj.arg

                while t < options['path_length']:
                    x = np.random.uniform(0, 1, size=2) < options['prt']
                    next_pos = obj.arg + diff * t * x

                    z = fn(next_pos)

                    if z < best_value:
                        best_value = z
                        best_pos = next_pos

                    t += options['step_size']

                new_population.append(Unit(arg=best_pos, cost=best_value))
            yield self.transform(new_population)
            population = new_population

        self.arg = leader.arg

    def find_leader(self, population):
        leader = population[0]
        for unit in population:
            if unit.cost < leader.cost:
                leader = unit

        return leader






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

