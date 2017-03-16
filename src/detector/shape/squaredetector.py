import cv2

from src.detector.shape.shapedetector import ShapeDetector
from detector.worldelement.shapefactory import NotASquareError


class SquareDetector(ShapeDetector):
    def __init__(self, shape_factory):
        super().__init__(shape_factory)

    def detect(self, image):
        squares = []
        for threshold_value in range(0, 255, 26):
            if threshold_value == 0:
                image = cv2.Canny(image, 100, 200)
                binary_image = cv2.dilate(image, None)
            else:
                return_value, binary_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)

            binary_image, contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            for contour_points in contours:
                polygon_points = self._approximate_polygon(contour_points)
                try:
                    square = self._shape_factory.create_square(polygon_points)
                    squares.append(square)
                except NotASquareError:
                    continue

        return squares
