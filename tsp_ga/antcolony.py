import random

from genetic import Evaluator, Trajectory
import numpy as np


class AntColony:
    def __init__(self, cities, popsize):
        self.evaluator = Evaluator(cities)
        self.cities = [(city.x, city.y) for city in cities]
        self.popsize = popsize

    def run(self):
        N = len(self.cities)

        alfa = 1
        beta = 1
        ro = 0.5
        Q = 100

        ants = list(range(N))
        all_cities = set(range(N))
        best = None

        feromones = np.ndarray((N, N))
        for i in range(N):
            for j in range(N):
                feromones[i, j] = 0.2

        for generation in range(100):
            paths = []
            for start in ants:
                trajectory = [start]
                print(feromones)

                while True:
                    to_check = all_cities - set(trajectory)
                    if not to_check:
                        new = Trajectory(trajectory, distance=self.evaluator.cost(trajectory))
                        if not best or best.distance > new.distance:
                            best = new
                            feromones = feromones

                        paths.append(new)
                        yield best, new
                        break

                    bottom = sum([feromones[start, j]**alfa * 1/self.evaluator.distances[start, j]**beta for j in to_check])
                    r = np.random.uniform()
                    cumulated = 0
                    for j in to_check:
                        cumulated += (feromones[start, j]**alfa * (1/self.evaluator.distances[start, j])**beta) / bottom

                        if cumulated >= r:
                            break

                    start = j
                    trajectory.append(start)

            feromones *= ro

            for new in paths:
                p = new.path + [new.path[0]]
                for a, b in zip(p, p[1:]):
                    feromones[a][b] += Q / new.distance
                    feromones[b][a] += Q / new.distance
