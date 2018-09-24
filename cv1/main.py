#!/usr/bin/env python3
import itertools
import time
import argparse
import sys

# vypsat trajektorie
# vypsat cas do ktereho to spocita


def trajectories(cities):
    if len(cities) < 1:
        yield []
    else:
        for perm in trajectories(cities[1:]):
            for i in range(len(cities)):
                yield list(perm[:i]) + [cities[0]] + list(perm[i:])


def print_all(N, permutate_fn):
    start = time.time()
    cities = range(N)

    print(f"Available trajectories for {N} cities")
    for trajectory in permutate_fn(cities):
        print(" -> ".join(map(lambda label: chr(label + ord('A')), trajectory)))

    elapsed = time.time() - start
    return elapsed

implementations = {
    'itertools': itertools.permutations,
    'recursive': trajectories
}

parser = argparse.ArgumentParser()
parser.add_argument("N", help="maximal number of cities", default=4, type=int, nargs='?')
parser.add_argument("--perm-impl", default='recursive', choices=implementations.keys())

args = parser.parse_args()

times = {}
for N in range(args.N + 1):
    times[N] = print_all(N, implementations[args.perm_impl])

print("\nResults", file=sys.stderr)
print("=======", file=sys.stderr)
print("\n".join(["{} - {:.5f}s".format(k, v) for k, v in times.items()]), file=sys.stderr)
