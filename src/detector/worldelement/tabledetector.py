import cv2
import numpy as np
from operator import methodcaller

from detector.shape.rectangledetector import RectangleDetector
from detector.worldelement.iworldelementdetector import IWorldElementDetector
from src.world.table import Table

MIN_TABLE_AREA = 70000


class NoTableFoundError(Exception):
    pass


class TableDetector(IWorldElementDetector):
    def __init__(self, shape_factory):
        self._shape_factory = shape_factory

    def detect(self, image):
        mask = self._threshold_table_color(image)
        table = self._find_table(mask)
        return table

    def _threshold_table_color(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_table_color = np.array([20, 10, 10])
        upper_table_color = np.array([40, 120, 240])
        mask = cv2.inRange(image, lower_table_color, upper_table_color)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=5)
        return mask

    def _find_table(self, image):
        rectangles = RectangleDetector(self._shape_factory).detect(image)
        rectangles = [rectangle for rectangle in rectangles if rectangle.area() > MIN_TABLE_AREA]
        rectangles = sorted(rectangles, key=methodcaller('area'), reverse=True)

        if len(rectangles) > 0:
            return Table(rectangles[0])
        else:
            raise NoTableFoundError
