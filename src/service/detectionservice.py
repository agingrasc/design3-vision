import glob
import cv2

from detector.worldelement.robotdetector import RobotDetector
from src.infrastructure.camera import JSONCameraModelRepository
from src.detector.worldelement.drawingareadetector import DrawingAreaDetector
from src.detector.worldelement.shapefactory import ShapeFactory
from src.detector.worldelement.tabledetector import TableDetector


class DetectionService:
    def __init__(self, drawing_area_detector, table_detector, robot_detector):
        self._detectors = [drawing_area_detector, table_detector, robot_detector]

    def detect_all_world_elements(self, image):
        world_elements = []

        for detector in self._detectors:
            try:
                world_element = detector.detect(image)
                world_elements.append(world_element)
            except Exception as e:
                print("World initialisation failure: {}".format(type(e).__name__))

        return world_elements

    def draw_world_elements_into(self, image, world_elements):
        for element in world_elements:
            element.draw_in(image)


if __name__ == '__main__':
    shape_factory = ShapeFactory()

    table_detector = TableDetector(shape_factory)
    drawing_area_detector = DrawingAreaDetector(shape_factory)
    robot_detector = RobotDetector()

    detection_service = DetectionService(drawing_area_detector, table_detector, robot_detector)
    camera_model_repository = JSONCameraModelRepository('../../data/camera_models/camera_models.json')
    camera_model = camera_model_repository.get_camera_model_by_id(0)

    for filename in glob.glob('../../data/images/full_scene/*.jpg'):
        image = cv2.imread(filename)

        image = camera_model.undistort_image(image)

        world_elements = detection_service.detect_all_world_elements(image)
        detection_service.draw_world_elements_into(image, world_elements)

        cv2.imshow('World Image', image)
        cv2.waitKey()
