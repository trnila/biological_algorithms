import random

import numpy as np

import algorithm_options
import algorithms
from algorithms import Algorithm, SimulationStep, Unit


class SomaDynamicPathLength(algorithms.Soma):
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

                # slower steps at begin
                while t < options['path_length'] * i**3 / options['migrations']**3 + options['step_size'] + 0.1:
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


class SomaFurthest(algorithms.Soma):
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

                # choose leader or furthest point
                if np.random.uniform(0, 1) < 0.1:
                    diff = leader.arg - obj.arg
                else:
                    diff = self.find_further(population, obj).arg - obj.arg

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

    def find_further(self, population, current):
        far = current
        max_dist = 0

        for unit in population:
            dist = np.linalg.norm(current.arg - unit.arg)
            if dist > max_dist:
                max_dist = dist
                far = unit

        return far

