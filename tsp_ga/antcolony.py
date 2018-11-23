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

        feromones = np.full((N, N), 0.2)

        for generation in range(100):
            paths = []
            for cur_city in ants:
                trajectory = [cur_city]

                while True:
                    remaining_cities = all_cities - set(trajectory)
                    if not remaining_cities:
                        new = Trajectory(trajectory, distance=self.evaluator.cost(trajectory))
                        if not best or best.distance > new.distance:
                            best = new

                        paths.append(new)
                        yield best, new
                        break

                    bottom = sum([feromones[cur_city, j]**alfa * 1/self.evaluator.distances[cur_city, j]**beta for j in remaining_cities])
                    r = np.random.uniform()
                    cumulated = 0
                    for j in remaining_cities:
                        cumulated += (feromones[cur_city, j]**alfa * (1/self.evaluator.distances[cur_city, j])**beta) / bottom

                        if cumulated >= r:
                            cur_city = j
                            trajectory.append(j)
                            break

            feromones *= ro

            for new in paths:
                p = new.path + [new.path[0]]
                for a, b in zip(p, p[1:]):
                    feromones[a][b] += Q / new.distance
                    feromones[b][a] += Q / new.distance
