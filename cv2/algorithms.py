import random

import numpy as np

import algorithm_options

class Unit:
    def __init__(self, arg, cost):
        self.arg = arg
        self.cost = cost

    def to_vec(self):
        return np.array([*self.arg, self.cost])

    def __repr__(self):
        return f"f({', '.join(map(str, self.arg))}) = {self.cost}"

INFINITY_UNIT = Unit(None, np.inf)

class SimulationStep:
    def __init__(self, points, best=None):
        self.points = points
        self.best = best


class Algorithm:
    def options(self):
        return []

    def find_leader(self, population):
        leader = population[0]
        for unit in population:
            if unit.cost < leader.cost:
                leader = unit

        return leader

    def get_better(self, a, b):
        return a if a.cost < b.cost else b


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
            'strategy': algorithm_options.ChoiceOption(['AllToOne', 'AllToAllRand']),
        }

    def run(self, space, fn, options):
        points = [space.gen_uniform_sample() for _ in range(options['pop_size'])]
        population = [Unit(arg=pos, cost=fn(pos)) for pos in points]

        leader = self.find_leader(population, options['strategy'])
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

            leader = self.find_leader(population, options['strategy'])
            yield SimulationStep(new_population, best=leader)

    def find_leader(self, population, strategy='AllToOne'):
        if strategy == 'AllToOne':
            return super(Soma, self).find_leader(population)

        return random.choice(population)



class PSO(Algorithm):
    def options(self):
        return {
            'migrations': algorithm_options.IntOption(default=100, min=2, max=100000),
            'pop_size': algorithm_options.IntOption(default=10, min=2, max=100000),

            'w_start': algorithm_options.FloatOption(default=0.9),
            'w_end': algorithm_options.FloatOption(default=0.4),

            'c1': algorithm_options.FloatOption(default=1),
            'c2': algorithm_options.FloatOption(default=1),
        }

    def run(self, space, fn, options):
        def make_unit(pos):
            unit = Unit(arg=pos, cost=fn(pos))
            unit.personal_best = unit
            unit.speed = random.uniform(0, (abs(space.sizes[0][0]) + abs(space.sizes[0][1]))/20)
            return unit

        population = [make_unit(space.gen_uniform_sample()) for _ in range(options['pop_size'])]
        gbest = self.find_leader(population)
        yield SimulationStep(population, best=gbest)

        for iteration in range(options['migrations']):
            new_population = []
            for unit in population:
                w = options['w_start'] - (options['w_start'] - options['w_end']) * iteration / options['migrations']

                new_speed = w * unit.speed + options['c1'] * random.uniform(0, 1) * (unit.personal_best.arg - unit.arg) \
                    + options['c2'] * random.uniform(0, 1) * (gbest.arg - unit.arg)
                new_pos = unit.arg + new_speed

                new_unit = space.make_unit(
                    new_pos, fn,
                    speed=new_speed
                )
                new_unit.personal_best = self.get_better(unit.personal_best, new_unit)
                gbest = self.get_better(gbest, new_unit)
                new_population.append(new_unit)

            population = new_population
            yield SimulationStep(population, best=gbest)


class DifferentialEvolution(Algorithm):
    STRATEGY_1 = 'DE/RAND/1/BIN'
    STRATEGY_2 = 'DE/current-to-pbest/1/BIN'

    def options(self):
        return {
            'generations': algorithm_options.IntOption(default=100, min=2, max=100000),
            'np': algorithm_options.IntOption(default=10, min=2, max=100000), # population size

            'F': algorithm_options.FloatOption(default=0.9),
            'cr': algorithm_options.FloatOption(default=0.9),
            'strategy': algorithm_options.ChoiceOption([self.STRATEGY_1, self.STRATEGY_2]),

            'p': algorithm_options.FloatOption(default=1.0, min=0.0, max=1.0),
        }

    def run(self, space, fn, options):
        def make_unit(pos):
            unit = Unit(arg=pos, cost=fn(pos))
            return unit

        population = [make_unit(space.gen_uniform_sample()) for _ in range(options['np'])]
        gbest = self.find_leader(population)
        yield SimulationStep(population, best=gbest)

        for generation in range(options['generations']):
            new_population = []
            for nth, unit in enumerate(population):
                seq = list(range(len(population)))
                seq.remove(nth)
                random.shuffle(seq)

                a = population[seq[0]]
                b = population[seq[1]]
                c = population[seq[2]]

                if options['strategy'] == self.STRATEGY_1:
                    noisy = c.arg + options['F'] * (a.arg - b.arg)
                elif options['strategy'] == self.STRATEGY_2:
                    # select all 100*p% percentile units and choose one of them
                    pbests = self.find_p_bests(population, options['p'])
                    pbest = random.choice(pbests)
                    noisy = unit.arg + options['F'] * (pbest.arg - unit.arg) + options['F'] * (a.arg - b.arg)
                else:
                    raise NotImplementedError("Unknown strategy: " + options['strategy'])

                new = np.zeros(len(a.arg))
                irand = random.randint(0, len(a.arg) - 1)
                for i in range(len(a.arg)):
                    # ensure that at least one parameter is used from noisy
                    if random.uniform(0, 1) < options['cr'] or i == irand:
                        new[i] = noisy[i]
                    else:
                        new[i] = unit.arg[i]

                candidate = space.make_unit(np.array(new), fn)
                if candidate.cost <= unit.cost:
                    new_population.append(candidate)
                else:
                    new_population.append(unit)

            population = new_population
            gbest = self.find_leader(population)
            yield SimulationStep(population, best=gbest)

    def find_p_bests(self, population, p):
        costs = [unit.cost for unit in population]
        threshold = np.percentile(costs, 100 * (1-p))
        return [unit for unit in population if unit.cost <= threshold]






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

