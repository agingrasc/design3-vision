import cv2
import numpy as np
from scipy.spatial import distance as dist
from domain.shape.square import Square

from domain.shape.rectangle import Rectangle


class NotASquareError(Exception):
    pass


class NotARectangleError(Exception):
    pass


class ShapeFactory:
    def create_square(self, points):
        if self._form_a_valid_square(points):
            center = self._find_center_of_mass(points)
            return Square(self._order_points(points), center)
        else:
            raise NotASquareError

    def create_rectangle(self, points):
        if self._form_a_valid_rectangle(points):
            return Rectangle(self._order_points(points))
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
        if max_cos < 0.04:
            return True
        else:
            return False

    def _angle_cos(self, p0, p1, p2):
        d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
        return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))

    # adapted from http://www.pyimagesearch.com/2016/03/21/ordering-coordinates-clockwise-with-python-and-opencv
    def _order_points(self, points):
        points = points[:, 0, :]
        x_sorted = points[np.argsort(points[:, 0]), :]

        left_most = x_sorted[:2, :]
        right_most = x_sorted[2:, :]

        left_most = left_most[np.argsort(left_most[:, 1]), :]
        (top_left, bottom_left) = left_most

        distance = dist.cdist(top_left[np.newaxis], right_most, "euclidean")[0]
        (bottom_right, top_right) = right_most[np.argsort(distance)[::-1], :]

        return np.array([top_left, top_right, bottom_right, bottom_left], dtype="int")

    def _find_center_of_mass(self, contour):
        contour_moments = cv2.moments(contour)
        center_x = int(contour_moments["m10"] / contour_moments["m00"])
        center_y = int(contour_moments["m01"] / contour_moments["m00"])
        return [center_x, center_y]