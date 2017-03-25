import cv2
from operator import methodcaller

import numpy as np

import config
from detector.shape.rectangledetector import RectangleDetector
from detector.worldelement.iworldelementdetector import IWorldElementDetector
from world.table import Table


class NoTableFoundError(Exception):
    pass


class TableDetector(IWorldElementDetector):
    def __init__(self, shape_factory):
        self._shape_factory = shape_factory

    def detect(self, image):
        mask = self._threshold_table_color(image)
        cv2.imshow('image', mask)
        table = self._find_table(mask)
        return table

    def _threshold_table_color(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image, config.LOWER_TABLE_COLOR, config.UPPER_TABLE_COLOR)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        return mask

    def _find_table(self, image):
        rectangles = RectangleDetector(self._shape_factory).detect(image)
        rectangles = [rectangle for rectangle in rectangles if rectangle.area() > config.MIN_TABLE_AREA]
        rectangles = sorted(rectangles, key=methodcaller('area'), reverse=True)

        if len(rectangles) > 0:
            return Table(rectangles[0])
        else:
            raise NoTableFoundError
