import cv2

from abc import ABCMeta
from abc import abstractmethod


class ShapeDetector(metaclass=ABCMeta):
    def __init__(self, shape_factory):
        self._shape_factory = shape_factory

    @abstractmethod
    def detect(self, image):
        pass

    def _approximate_polygon(self, contour_points):
        contour_length = cv2.arcLength(contour_points, True)
        polygon_points = cv2.approxPolyDP(contour_points, 0.02 * contour_length, True)
        return polygon_points
