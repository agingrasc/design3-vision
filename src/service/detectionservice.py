import cv2

from src.detector.drawingareadetector import DrawingAreaDetector
from src.detector.shapefactory import ShapeFactory


class DetectionService:
    def __init__(self, drawing_area_detector):
        self._drawing_area_detector = drawing_area_detector

    def detect_world_elements(self, image):
        elements = []
        drawing_area = self._drawing_area_detector.detect(image)
        elements.append(drawing_area)
        return elements


if __name__ == '__main__':
    image = cv2.imread('../../data/images/robot_images/image10.jpg')

    shape_factory = ShapeFactory()
    drawing_area_detector = DrawingAreaDetector(shape_factory)
    detection_service = DetectionService(drawing_area_detector)

    world_elements = detection_service.detect_world_elements(image)

    for element in world_elements:
        element.draw_in(image)

    cv2.imshow('World Image', image)
    cv2.waitKey()
