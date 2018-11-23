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
        initial_feromones = 0.2
        max_generations = 100

        all_cities = set(range(N))
        best = None

        feromones = np.full((N, N), initial_feromones)

        for generation in range(max_generations):
            paths = []
            # each ant starts in different city
            for cur_city in all_cities:
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

                    def cost(candidate):
                        return feromones[cur_city, candidate]**alfa * 1/self.evaluator.distances[cur_city, candidate]**beta

                    bottom = sum(map(cost, remaining_cities))
                    cumulated = 0
                    r = np.random.uniform()
                    for j in remaining_cities:
                        cumulated += cost(j) / bottom

                        if cumulated >= r:
                            cur_city = j
                            trajectory.append(j)
                            break

            # decay all feromones
            feromones *= ro

            # strengthen feromones on used paths
            for path in paths:
                p = path.path + [path.path[0]]
                for a, b in zip(p, p[1:]):
                    feromones[a][b] += Q / path.distance
                    feromones[b][a] += Q / path.distance
