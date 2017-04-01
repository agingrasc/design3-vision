import cv2
import numpy as np

from domain.geometry.coordinate import Coordinate


class Square:
    def __init__(self, points, center):
        self._contour_points = points.tolist()
        self._center = center

    def area(self):
        return cv2.contourArea(self.as_contour_points())

    def as_contour_points(self):
        return np.array(self._contour_points)

    def as_coordinates(self):
        return [Coordinate(point[0], point[1]) for point in self._contour_points]

    def draw_in(self, image):
        cv2.drawContours(image, [self.as_contour_points()], 0, (0, 0, 255), 2)
