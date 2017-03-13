import base64
import glob
import json
import cv2
from websocket import create_connection

from detector.worldelement.drawingareadetector import DrawingAreaDetector
from detector.worldelement.robotdetector import RobotDetector
from detector.worldelement.shapefactory import ShapeFactory
from detector.worldelement.tabledetector import TableDetector
from infrastructure.camera import JSONCameraModelRepository
from service.image.imagedetectionservice import ImageToWorldTranslator, ImageDetectionService

if __name__ == "__main__":
    camera_model_repository = JSONCameraModelRepository('./data/camera_models/camera_models.json')
    camera_model = camera_model_repository.get_camera_model_by_id(0)
    image_to_world_translator = ImageToWorldTranslator(camera_model)

    shape_factory = ShapeFactory()

    table_detector = TableDetector(shape_factory)
    drawing_area_detector = DrawingAreaDetector(shape_factory)
    robot_detector = RobotDetector(shape_factory)

    detection_service = ImageDetectionService(drawing_area_detector, table_detector, robot_detector,
                                              image_to_world_translator)

    for filename in glob.glob('./data/images/full_scene/*.jpg'):
        image = cv2.imread(filename)
        image = camera_model.undistort_image(image)

        world = detection_service.translate_image_to_world(image)

        cv2.imshow('World Image', image)
        cv2.waitKey()
    #
    # connection = create_connection("ws://localhost:3000")
    #
    # APP_OPEN = True
    # while APP_OPEN:
    #     connection.send()
