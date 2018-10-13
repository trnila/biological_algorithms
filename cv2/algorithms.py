import numpy as np

import algorithm_options

class Unit:
    def __init__(self, arg, cost):
        self.arg = arg
        self.cost = cost

    def to_vec(self):
        return np.array([*self.arg, self.cost])

INFINITY_UNIT = Unit(None, np.inf)

class SimulationStep:
    def __init__(self, points, best=None):
        self.points = points
        self.best = best


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
        extreme = INFINITY_UNIT
        for i in range(options['iterations']):
            next_unit = space.gen_uniform_unit(fitness)

            if next_unit.cost < extreme.cost:
                extreme = next_unit

            yield SimulationStep([next_unit], best=extreme)


class ClimbingSearch(Algorithm):
    def options(self):
        return {
            'iterations': algorithm_options.IntOption(default=100, min=1, max=1000),
            'population': algorithm_options.IntOption(default=20, min=1, max=1000),
            'sigma': algorithm_options.FloatOption(default=0.1, min=0.0, max=1000),
            'start_position': algorithm_options.StartPositionOption()
        }

    def run(self, space, fn, options):
        center = space.gen_uniform_unit(fn)
        if options['start_position']:
            center = options['start_position']

        extreme = INFINITY_UNIT
        for i in range(options['iterations']):
            points = []
            for x in range(options['population']):
                p = space.gen_unit_in_range(fn, lambda: center.arg + np.random.randn(2) * options['sigma'])
                points.append(p)
                if p.cost < extreme.cost:
                    extreme = p

            center = extreme
            yield SimulationStep(points, best=extreme)


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
        x0 = space.gen_uniform_unit(fn)
        if options['start_position']:
            x0 = np.array(options['start_position'])

        T = options['initial_temp']
        while T > options['final_temp']:
            x = space.gen_unit_in_range(fn, lambda: x0.arg + np.random.randn(2) * options['sigma'])

            # take better solution
            if x.cost < x0.cost:
                x0 = x
            else:
                r = np.random.uniform(0, 1)
                if r < np.exp(-(x.cost - x0.cost)/T):
                    x0 = x

            yield SimulationStep([x0], best=x0)

            # reduce temperature
            T *= options['alpha']


class Soma(Algorithm):
    def options(self):
        return {
            'path_length': algorithm_options.FloatOption(default=3.0, min=0.1, max=100000),
            'step_size': algorithm_options.FloatOption(default=0.11, min=0.0000000001, max=100000),
            'pop_size': algorithm_options.IntOption(default=10, min=2, max=100000),
            'prt': algorithm_options.FloatOption(default=0.1),
            'migrations': algorithm_options.IntOption(default=10, min=2, max=100000),
        }

    def run(self, space, fn, options):
        points = [space.gen_uniform_sample() for _ in range(options['pop_size'])]
        population = [Unit(arg=pos, cost=fn(pos)) for pos in points]

        leader = self.find_leader(population)
        yield SimulationStep(population, best=leader)

        for i in range(options['migrations']):
            new_population = []
            for obj in population:
                best_pos = None
                best_value = np.inf
                t = options['step_size']

                diff = leader.arg - obj.arg

                while t < options['path_length']:
                    x = np.random.uniform(0, 1, size=2) < options['prt']
                    next_pos = obj.arg + diff * t * x
                    if space.in_range(next_pos):
                        z = fn(next_pos)

                        if z < best_value:
                            best_value = z
                            best_pos = next_pos

                    t += options['step_size']

                new_population.append(Unit(arg=best_pos, cost=best_value))
            population = new_population

            leader = self.find_leader(population)
            yield SimulationStep(new_population, best=leader)

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

