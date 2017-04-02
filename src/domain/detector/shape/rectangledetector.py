import cv2

from domain.detector.shape.shapedetector import ShapeDetector
from domain.detector.worldelement.shapefactory import NotARectangleError


class RectangleDetector(ShapeDetector):
    def __init__(self, shape_factory):
        super().__init__(shape_factory)

    def detect(self, image):
        rectangles = []
        binary_image, contours, hierarchy = cv2.findContours(image.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for contour_points in contours:
            polygon_points = self._approximate_polygon(contour_points)

            try:
                rectangle = self._shape_factory.create_rectangle(polygon_points)
                rectangles.append(rectangle)
            except NotARectangleError:
                pass

        return rectangles
