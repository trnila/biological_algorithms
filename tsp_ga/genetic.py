import math
import random

import numpy as np

from common import Trajectory, Evaluator


class Genetic:
    def __init__(self, cities, popsize):
        self.evaluator = Evaluator(cities)
        self.cities = [(city.x, city.y) for city in cities]
        self.popsize = popsize

    def select(self, population):
        distances = [trajectory.distance for trajectory in population]
        m = min(distances)
        M = max(distances)

        costs = sorted([(1 - (trajectory.distance - m) / (M - m+0.0001), i, trajectory.distance) for i, trajectory in enumerate(population)], key=lambda x: x[0])

        first = None
        r = np.random.uniform()
        for x in costs:
            if x[0] >= r:
                first = x[1]
                costs.remove(x)
                break

        r = np.random.uniform()
        for x in costs:
            if x[0] >= r:
                return first, x[1]

        return first, costs[-1][1]

    def run(self, opts):
        def make_trajectory():
            trajectory = list(range(len(self.cities)))
            random.shuffle(trajectory)

            return Trajectory(trajectory, self.evaluator.cost(trajectory))

        population = [make_trajectory() for i in range(self.popsize)]

        glob_best = None
        not_changed = 0
        while not_changed < 1000:
            new_pop = [glob_best] if glob_best else []

            for i in range(self.popsize - 1):
                first, second = self.select(population)
                parent1 = population[first].path
                parent2 = population[second].path

                new = self.merge(parent1, parent2)
                new = self.mutate(new)
                new = Trajectory(new, self.evaluator.cost(new))

                new_pop.append(new)

                for trajectory in population:
                    if glob_best is None or trajectory.distance < glob_best.distance:
                        glob_best = trajectory

                yield (glob_best, new)

            population = new_pop

    def mutate(self, cities):
        cities = cities.copy()
        a, b = self.rand_two()

        cities[a], cities[b] = cities[b], cities[a]
        return cities

    def rand_two(self):
        to_choose = list(range(0, len(self.cities)))
        a = random.choice(to_choose)
        to_choose.remove(a)
        b = random.choice(to_choose)
        return a, b

    def merge(self, a, b):
        left = random.randint(0, len(self.cities) - 1)
        right = random.randint(left + 1, len(self.cities))

        new = [None for i in range(len(a))]

        for i in range(left + 1):
            new[i] = a[i]

        for i in range(right, len(a)):
            new[i] = a[i]

        j = 0
        i = left + 1
        while i < right:
            while True:
                if b[j] not in new:

                    if new[i]:
                        raise "xxx"
                    new[i] = b[j]
                    break
                j += 1
            i += 1

        return new


class Geneticx:
    def __init__(self, cities):
        self.cities = cities
        #np.random.seed(1)
        #random.seed(1)

        self.evaluator = Evaluator(cities)

    def cost(self, trajectory):
        total = 0
        prev = trajectory[-1]
        for city in trajectory:
            total += self.distances[prev.id][city.id]

        return total

    def run(self):
        population = self.cities

        yield Trajectory(population, self.cost(population))

        while True:
            parent = self.mutate(population)
            new = self.merge(parent, population)
            yield Trajectory(new, self.cost(new))

            if self.cost(new) < self.cost(population):
                population = new

    def merge(self, a, b):
        left = random.randint(0, len(self.cities) - 1)
        right = random.randint(left + 1, len(self.cities))


        new = [None for i in range(len(a))]

        for i in range(left + 1):
            new[i] = a[i]

        for i in range(right, len(a)):
            new[i] = a[i]

        j = 0
        i = left + 1
        while i < right:
            while True:
                if b[j] not in new:

                    if new[i]:
                        raise "xxx"
                    new[i] = b[j]
                    break
                j += 1
            i += 1

        return new


    def mutate(self, cities):
        cities = cities.copy()
        a, b = self.rand_two()

        cities[a], cities[b] = cities[b], cities[a]
        return cities

    def rand_two(self):
        to_choose = list(range(0, len(self.cities)))
        a = random.choice(to_choose)
        to_choose.remove(a)
        b = random.choice(to_choose)
        return a, b