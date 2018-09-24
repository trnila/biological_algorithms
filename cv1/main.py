#!/usr/bin/env python3
import itertools
import time
import argparse
import sys

# vypsat trajektorie
# vypsat cas do ktereho to spocita


def impl_reclist(cities):
    if len(cities) < 1:
        yield []
    else:
        for perm in impl_reclist(cities[1:]):
            for i in range(len(cities)):
                yield list(perm[:i]) + [cities[0]] + list(perm[i:])

def impl_heap(cities):
    def fn(cities, n):
        if n == 1:
            yield cities
        else:
            for i in range(len(cities)):
                yield from fn(cities, n - 1)
                if n & 1 == 0:
                    cities[i], cities[n - 1] = cities[n - 1], cities[i]
                else:
                    cities[0], cities[n - 1] = cities[n - 1], cities[0]
    yield from fn(cities, len(cities))


def print_all(N, permutate_fn):
    start = time.time()
    cities = list(range(N))

    print(f"Available trajectories for {N} cities")
    for trajectory in permutate_fn(cities):
        print(" -> ".join(map(lambda label: chr(label + ord('A')), trajectory)))

    elapsed = time.time() - start
    return elapsed

implementations = {
    'itertools': itertools.permutations,
    'reclist': impl_reclist,
    'heap': impl_heap,
}

parser = argparse.ArgumentParser()
parser.add_argument("N", help="maximal number of cities", default=4, type=int, nargs='?')
parser.add_argument("--perm-impl", default='reclist', choices=implementations.keys())

args = parser.parse_args()

times = {}
for N in range(args.N + 1):
    times[N] = print_all(N, implementations[args.perm_impl])

print("\nResults", file=sys.stderr)
print("=======", file=sys.stderr)
print("\n".join(["{} - {:.5f}s".format(k, v) for k, v in times.items()]), file=sys.stderr)
