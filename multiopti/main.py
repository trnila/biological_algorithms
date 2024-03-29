import numpy as np
import matplotlib.pyplot as plt
import random
import time

def nondominated_sort(P):
    v_f1 = f1(P)
    v_f2 = f2(P)

    n = [0 for i in range(len(P))]
    S = [set() for i in range(len(P))]
    ranks = [0 for i in range(len(P))]
    fronts = [set() for i in range(len(P))]

    for p in range(len(P)):
        for q in range(len(P)):
            if p == q:
                continue

            if v_f1[p] >= v_f1[q] and v_f2[p] >= v_f2[q]:
                S[p].add(q)
            elif v_f1[q] >= v_f1[p] and v_f2[q] >= v_f2[p]:
                n[p] += 1

        if n[p] == 0:
            ranks[p] = 1
            fronts[0].add(p)

    i = 0
    while len(fronts[i]) > 0 and i + 1 < len(P):
        Q = set()
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    ranks[q] += 1
                    Q.add(q)

        i += 1
        fronts[i] = Q

    return fronts


def graph(points):
    xs = [i for i in points]
    ys = []

    for x in xs:
        if f1(x) > f2(x):
            ys.append(f1(x))
        else:
            ys.append(f2(x))

    plt.scatter(xs, ys)


def assign(I):
    distances = [0 for i in range(len(I))]

    for fn in [f1, f2]:
        I = sorted(I, key=fn)

        distances[0] = distances[-1] = 10000000
        for i in range(1, len(I) - 1):
            distances[i] += fn(I[i + 1]) - fn(I[i - 1])

    return sorted(zip(distances, I))

def select(pop):
    vals = [val for val, _ in pop]
    m = min(vals)
    M = max(vals)

    def fit(val):
        return (val - m) / (M - m + 0.000001)

    fitness = [(fit(cost), x) for cost, x in pop]

    r = random.uniform(0, 1)
    cumsum = 0
    for prop, x in fitness:
        cumsum += prop
        if cumsum > r:
            return pop[0][1], x

    return pop[0][1], pop[1][1]

def crossover(a, b):
    return (a + b) / 2


def mutate(a):
    return a + np.random.normal()


def evolution(pop):
    evoluted = []

    for i in range(len(pop)):
        a, b = select(pop)
        evoluted.append(mutate(crossover(a, b)))

    return evoluted

start, end = -60, 60
NP = 20

f1 = lambda x: -x**2
f2 = lambda x: -(x-2)**2

x = np.linspace(start, end, 1000)

# create initial population
#P = np.array([-2, -1, 0, 2, 4, 1])
P = np.random.uniform(start, end, size=NP)

for generation in range(1, 20):
    fronts = nondominated_sort(P)
    print("fronts", fronts)

    new_pop = []
    i = 0
    while len(new_pop) + len(fronts[i]) < NP:
        for cost, idx in assign(fronts[i]):
            new_pop.append((cost, P[idx]))
        i += 1

    for cost, idx in assign(fronts[i])[0:NP - len(new_pop)]:
        new_pop.append((cost, P[idx]))

    P = np.array(list([x for _, x in new_pop]) + evolution(new_pop))
    print("P", P)

    plt.clf()
    plt.subplot(2, 1, 1)
    plt.plot(x, f1(x))
    plt.plot(x, f2(x))
    for p in fronts:
        graph([P[i] for i in p])

    plt.subplot(2, 1, 2)
    plt.xlim([-1, 3])
    plt.ylim([-4, 1])
    plt.plot(x, f1(x))
    plt.plot(x, f2(x))
    for p in fronts:
        graph([P[i] for i in p])

    plt.show()
    time.sleep(1)
