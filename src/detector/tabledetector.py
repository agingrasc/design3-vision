import cv2
import numpy as np
from operator import methodcaller

from world.table import Table
from detector.shapedetector import RectangleDetector


class NoTableFound(Exception):
    pass


class TableDetector:
    def __init__(self, shape_factory):
        self._shape_factory = shape_factory

    def detect(self, image):
        mask = self._threshold_table_color(image)
        table = self._find_table(mask)
        return table

    def _threshold_table_color(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_green_hsv = np.array([20, 10, 10])
        upper_green_hsv = np.array([40, 120, 240])
        mask = cv2.inRange(image, lower_green_hsv, upper_green_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
        return mask

    def _find_table(self, image):
        rectangles = RectangleDetector(self._shape_factory).detect(image)
        rectangles = [rectangle for rectangle in rectangles if rectangle.area() > 70000]
        rectangles = sorted(rectangles, key=methodcaller('area'), reverse=True)

        if len(rectangles) > 0:
            return Table(rectangles[0])
        else:
            raise NoTableFound
