import numpy as np

from unittest import TestCase

from shape.rectangle import Rectangle
from shape.square import Square
from detector.worldelement.shapefactory import ShapeFactory, NotASquareError, NotARectangleError


class ShapeFactoryTest(TestCase):
    def setUp(self):
        self.five_points = np.array([[0, 0], [0, 50], [50, 50], [50, 0], [100, 0]])
        self.three_points = np.array([[0, 0], [0, 50], [50, 50]])
        self.shape_factory = ShapeFactory()

    def test_given_valid_square_points_when_creating_a_square_then_a_square_is_created(self):
        valid_square_points = np.array([[0, 0], [0, 50], [50, 50], [50, 0]])

        square = self.shape_factory.create_square(valid_square_points)

        self.assertIsInstance(square, Square)

    def test_given_too_many_points_when_creating_a_square_then_an_error_is_thrown(self):
        self.assertRaises(NotASquareError, self.shape_factory.create_square, self.five_points)

    def test_given_too_few_points_when_creating_a_square_then_an_error_is_thrown(self):
        self.assertRaises(NotASquareError, self.shape_factory.create_square, self.three_points)

    def test_given_four_points_not_making_a_square_when_creating_a_square_then_an_error_is_thrown(self):
        four_points_not_forming_a_square = np.array([[0, 0], [0, 50], [100, 50], [100, 0]])

        self.assertRaises(NotASquareError, self.shape_factory.create_square, four_points_not_forming_a_square)

    def test_given_four_points_not_making_right_angles_when_creating_a_square_then_an_error_is_thrown(self):
        four_points_not_making_right_angles = np.array([[0, 0], [0, 50], [100, 50], [50, 0]])

        self.assertRaises(NotASquareError, self.shape_factory.create_square, four_points_not_making_right_angles)

    def test_given_valid_rectangle_points_when_creating_a_rectangle_then_a_rectangle_is_created(self):
        valid_rectangle_points = np.array([[0, 0], [0, 50], [100, 50], [100, 0]])

        a_rectangle = self.shape_factory.create_rectangle(valid_rectangle_points)

        self.assertIsInstance(a_rectangle, Rectangle)

    def test_given_too_many_points_when_creating_a_rectangle_then_an_error_is_thrown(self):
        self.assertRaises(NotARectangleError, self.shape_factory.create_rectangle, self.five_points)

    def test_given_too_few_points_when_creating_a_rectangle_then_an_error_is_thrown(self):
        self.assertRaises(NotARectangleError, self.shape_factory.create_rectangle, self.three_points)

    def test_given_four_points_not_making_a_rectangle_when_creating_a_rectangle_then_an_error_is_thrown(self):
        four_points_not_forming_a_rectangle = np.array([[0, 0], [0, 50], [50, 50], [50, 0]])

        self.assertRaises(NotARectangleError, self.shape_factory.create_rectangle, four_points_not_forming_a_rectangle)

    def test_given_four_points_not_making_right_angles_when_creating_a_rectangle_then_an_error_is_thrown(self):
        four_points_not_making_right_angles = np.array([[0, 0], [0, 50], [50, 50], [100, 0]])

        self.assertRaises(NotARectangleError, self.shape_factory.create_rectangle, four_points_not_making_right_angles)
