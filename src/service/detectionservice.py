import cv2

from detector.drawingareadetector import DrawingAreaDetector
from detector.robotpositiondetector import RobotPositionDetector


class DetectionService:
    def __init__(self, drawing_area_detector, robot_position_detector):
        self._drawing_area_detector = drawing_area_detector
        self._robot_detector = robot_position_detector

    def detect_world_elements(self, image):
        elements = []
        drawing_area = self._drawing_area_detector.detect(image)
        robot_position = self._robot_detector.detect_position(image)
        elements.append(drawing_area)
        elements.append(robot_position)
        return elements


if __name__ == '__main__':
    drawing_area_detector = DrawingAreaDetector()
    robot_position_detector = RobotPositionDetector()
    detection_service = DetectionService(drawing_area_detector, robot_position_detector)

    image = cv2.imread('../../data/images/robot_images/image10.jpg')

    world_elements = detection_service.detect_world_elements(image)
