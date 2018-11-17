import math
import random

import numpy as np


class Trajectory:
    def __init__(self, path, distance):
        self.path = path
        self.distance = distance

    def __repr__(self):
        return f"({self.distance}) {self.path}"


class Evaluator:
    def __init__(self, cities):
        self.hops = len(cities)
        self.distances = np.ndarray((len(cities), len(cities)))
        for city1 in cities:
            for city2 in cities:
                x = abs(city1.x - city2.x)
                y = abs(city1.y - city2.y)
                self.distances[city1.id, city2.id] = math.sqrt(x * x + y * y)

    def cost(self, trajectory):
        if len(trajectory) != self.hops:
            raise ValueError(f"Trajectory must be composed from {self.hops} hops")

        total = 0
        prev = trajectory[-1]
        for city in trajectory:
            total += self.distances[prev, city]
            prev = city

        return total


class Genetic:
    def __init__(self, cities):
        self.evaluator = Evaluator(cities)
        self.cities = [(city.x, city.y) for city in cities]
        self.popsize = 800

    def select(self, population):
        distances = [trajectory.distance for trajectory in population]
        m = min(distances)
        M = max(distances)

        costs = sorted([(1 - (trajectory.distance - m) / (M - m+0.0001), i, trajectory.distance) for i, trajectory in enumerate(population)], key=lambda x: x[0])


        r = np.random.uniform()

        for x in costs:
            if x[0] >= r:
                return x[1]

        raise "Error"



    def run(self):
        def make_trajectory():
            trajectory = list(range(len(self.cities)))
            random.shuffle(trajectory)

            return Trajectory(trajectory, self.evaluator.cost(trajectory))

        population = [make_trajectory() for i in range(self.popsize)]

        while True:
            parent1 = population[self.select(population)].path
            parent2 = population[self.select(population)].path

            new = self.merge(parent1, parent2)
            self.mutate(new)
            new = Trajectory(new, self.evaluator.cost(new))

            population.append(new)


            best = population[0]
            worst = population[0]

            for trajectory in population:
                if trajectory.distance < best.distance:
                    best = trajectory

                if trajectory.distance > worst.distance:
                    worst = trajectory

            population.remove(worst)

            yield (best, new)

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