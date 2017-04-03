import math

from unittest import TestCase

from domain.geometry.coordinate import Coordinate


class CoordinateTest(TestCase):
    def test_given_a_coordinate_when_asking_the_distance_from_another_coordinate_then_returns_the_distance(self):
        a_coordinate = Coordinate(10, 10)
        another_coordinate = Coordinate(15, 15)
        expected_distance = math.sqrt((5 ** 2) + (5 ** 2))

        self.assertEqual(expected_distance, a_coordinate.distance_from(another_coordinate))
