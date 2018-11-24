from unittest import TestCase


from collections import namedtuple
from common import Evaluator

City = namedtuple('City', ['x', 'y', 'name', 'id'])


class TestEvaluator(TestCase):
    def test_cost(self):
        cities = [
            City(10, 10, 'A', 0),
            City(20, 10, 'B', 1),
            City(20, 20, 'C', 2),
            City(10, 20, 'D', 3),
        ]

        evaluator = Evaluator(cities)

        self.assertEqual(40, evaluator.cost([0, 1, 2, 3]))
        self.assertEqual(40, evaluator.cost([3, 2, 1, 0]))
        self.assertEqual(48.2842712474619, evaluator.cost([0, 2, 3, 2]))
