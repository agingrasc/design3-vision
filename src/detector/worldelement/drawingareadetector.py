import cv2
import numpy as np
from sklearn.cluster import KMeans

from detector.shape.squaredetector import SquareDetector
from detector.worldelement.worldelementdetector import WorldElementDetector
from src.world.drawingarea import DrawingArea


class NoDrawingAreaFoundError(Exception):
    pass


def closest_node(node, nodes):
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node) ** 2, axis=1)
    return np.argmin(dist_2)


class DrawingAreaDetector(WorldElementDetector):
    def __init__(self, shape_factory):
        super().__init__(shape_factory)

    def detect(self, image):
        image = self._preprocess(image)
        mask = self._threshold_green(image)
        drawing_area = self._find_drawing_area(mask)
        return drawing_area

    def _preprocess(self, image):
        image = cv2.medianBlur(image, ksize=3)
        return image

    def _threshold_green(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_green_hsv = np.array([45, 40, 40])
        upper_green_hsv = np.array([80, 255, 255])
        mask = cv2.inRange(image, lower_green_hsv, upper_green_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=3)
        return mask

    def _find_drawing_area(self, image):
        squares = SquareDetector(self._shape_factory).detect(image)
        if len(squares) > 0:
            inner, outer = self._get_inner_and_outer_edges(squares)
            return DrawingArea(inner, outer)
        else:
            raise NoDrawingAreaFoundError

    def _get_inner_and_outer_edges(self, squares):
        sq = np.array([[2, square.area()] for square in squares])

        kmeans = KMeans(n_clusters=2, random_state=0).fit(sq)

        mean_inner_square = kmeans.cluster_centers_[0]
        mean_outer_square = kmeans.cluster_centers_[1]

        inner_index = closest_node(mean_inner_square, sq)
        outer_index = closest_node(mean_outer_square, sq)

        return squares[inner_index], squares[outer_index]
