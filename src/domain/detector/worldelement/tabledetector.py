from operator import methodcaller

import cv2

import config
from domain.detector.shape.rectangledetector import RectangleDetector
from domain.detector.worldelement.iworldelementdetector import IWorldElementDetector
from domain.world.table import Table


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
        mask = cv2.adaptiveThreshold(cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY), 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return mask

    def _find_table(self, image):
        rectangles = RectangleDetector(self._shape_factory).detect(image)
        rectangles = [rectangle for rectangle in rectangles if rectangle.area() > config.MIN_TABLE_AREA]
        rectangles = sorted(rectangles, key=methodcaller('area'), reverse=True)

        if len(rectangles) > 0:
            return Table(rectangles[0])
        else:
            raise NoTableFoundError
