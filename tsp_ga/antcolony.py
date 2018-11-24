from common import Trajectory, Evaluator
import numpy as np


class AntColony:
    defaults = {
        'alfa': 1,
        'beta': 1,
        'ro': 0.5,
        'Q': 100,
        'initial_pheromones': 0.2,
        'max_generations': 100
    }

    def __init__(self, cities, popsize):
        self.evaluator = Evaluator(cities)
        self.cities = [(city.x, city.y) for city in cities]
        self.popsize = popsize

    def run(self, opts):
        for key in opts.keys():
            if key not in self.defaults:
                raise KeyError(f"Unknown parameter '{key}'")
        opts = {**self.defaults, **opts}

        N = len(self.cities)
        all_cities = set(range(N))
        best = None
        pheromones = np.full((N, N), opts['initial_pheromones'])

        for generation in range(opts['max_generations']):
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

                    cur_city = self.choose_next_path(pheromones, cur_city, remaining_cities, opts)
                    trajectory.append(cur_city)

            self.update_pheromones(pheromones, paths, opts)

    def choose_next_path(self, pheromones, cur_city, remaining_cities, opts):
        def cost(candidate):
            return pheromones[cur_city, candidate] ** opts['alfa'] * 1 / self.evaluator.distances[cur_city, candidate] ** opts['beta']

        bottom = sum(map(cost, remaining_cities))
        cumulated = 0
        r = np.random.uniform()
        for j in remaining_cities:
            cumulated += cost(j) / bottom

            if cumulated >= r:
                return j

    def update_pheromones(self, pheromones, paths, opts):
        # decay all pheromones
        pheromones *= opts['ro']
        # strengthen pheromones on used paths
        for path in paths:
            p = path.path + [path.path[0]]
            for a, b in zip(p, p[1:]):
                pheromones[a][b] += opts['Q'] / path.distance
                pheromones[b][a] += opts['Q'] / path.distance
