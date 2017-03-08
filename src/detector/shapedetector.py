import cv2

from src.detector.shapefactory import NotASquareError


class SquareDetector:
    def __init__(self, shape_factory):
        self._shape_factory = shape_factory

    def detect(self, image):
        squares = []
        for threshold_value in range(0, 255, 26):
            if threshold_value == 0:
                image = cv2.Canny(image, 100, 200)
                binary_image = cv2.dilate(image, None)
                cv2.imshow('Square', binary_image)
            else:
                retval, binary_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)

            binary_image, contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            for contour_points in contours:
                polygone_points = self._approximate_polygone(contour_points)
                try:
                    square = self._shape_factory.create_square(polygone_points)
                    squares.append(square)
                except NotASquareError:
                    continue

        return squares

    def _approximate_polygone(self, contour_points):
        contour_length = cv2.arcLength(contour_points, True)
        polygone_points = cv2.approxPolyDP(contour_points, 0.02 * contour_length, True)
        return polygone_points
