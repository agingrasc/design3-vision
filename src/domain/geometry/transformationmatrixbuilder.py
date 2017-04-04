import math

from numpy import array, dot, deg2rad
from numpy.linalg import inv


class TransformationMatrixBuilder:
    def __init__(self):
        self._transformation_matrix = array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

    def rotate(self, angle):
        angle_in_rad = deg2rad(angle)

        self._transformation_matrix = dot(array([
            [math.cos(angle_in_rad), -1 * math.sin(angle_in_rad), 0],
            [math.sin(angle_in_rad), math.cos(angle_in_rad), 0],
            [0, 0, 1]
        ]), self._transformation_matrix)

        return self

    def scale(self, scale_factor):
        self._transformation_matrix = dot(array([
            [scale_factor, 0, 0],
            [0, scale_factor, 0],
            [0, 0, 1]
        ]), self._transformation_matrix)

        return self

    def translate(self, x, y):
        self._transformation_matrix = dot(array([
            [1, 0, x],
            [0, 1, y],
            [0, 0, 1]
        ]), self._transformation_matrix)

        return self

    def inverse(self):
        self._transformation_matrix = inv(self._transformation_matrix)
        return self

    def build(self):
        return self._transformation_matrix
