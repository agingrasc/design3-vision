import cv2
import numpy as np

from shape.rectangle import Rectangle
from shape.square import Square


class NotASquareError(Exception):
    pass


class NotARectangleError(Exception):
    pass


class ShapeFactory:
    def create_square(self, points):
        if self._form_a_valid_square(points):
            return Square(points)
        else:
            raise NotASquareError

    def create_rectangle(self, points):
        if self._form_a_valid_rectangle(points):
            return Rectangle(points)
        else:
            raise NotARectangleError

    def _form_a_valid_square(self, points):
        return self._points_have_four_sides(points) and self._have_all_right_angles(
            points) and self._sides_form_a_square(points)

    def _form_a_valid_rectangle(self, points):
        return self._points_have_four_sides(points) and self._have_all_right_angles(
            points) and self._sides_form_a_rectangle(points)

    def _points_have_four_sides(self, points):
        return len(points) == 4 and cv2.contourArea(points) > 1000 and cv2.isContourConvex(points)

    def _sides_form_a_square(self, points):
        (x, y, w, h) = cv2.boundingRect(points)
        ar = w / float(h)
        return ar >= 0.95 and ar <= 1.05

    def _sides_form_a_rectangle(self, points):
        (x, y, w, h) = cv2.boundingRect(points)
        ar = w / float(h)
        return ar > 1.05

    def _have_all_right_angles(self, points):
        points = points.reshape(-1, 2)
        max_cos = np.max(
            [self._angle_cos(points[i], points[(i + 1) % 4], points[(i + 2) % 4]) for i in range(0, 4)])
        if max_cos < 0.1:
            return True
        else:
            return False

    def _angle_cos(self, p0, p1, p2):
        d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
        return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))
