import math

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