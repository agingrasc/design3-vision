import base64
import json
import cv2

from enum import Enum
from websocket import create_connection

from detector.worldelement.drawingareadetector import DrawingAreaDetector
from detector.worldelement.robotdetector import RobotDetector
from detector.worldelement.shapefactory import ShapeFactory
from detector.worldelement.tabledetector import TableDetector
from infrastructure.camera import JSONCameraModelRepository
from infrastructure.imagesource.directoryimagesource import DirectoryImageSource
from infrastructure.imagesource.videostreamimagesource import VideoStreamImageSource
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagedetectionservice import ImageToWorldTranslator
from service.image.imagedetectionservice import ImageDetectionService

import config

AppEnvironment = Enum('AppEnvironment', 'TESTING_VISION, COMPETITION, DEBUG')


def get_world_dimension(world):
    if world is not None:
        return {
            "width": str(world._width),
            "height": str(world._length)
        }
    else:
        return {
            "width": "",
            "height": ""
        }


def get_world_origin(world):
    if world is not None:
        return {
            "x": str(world._image_origin._x / 2),
            "y": str(world._image_origin._y / 2)
        }
    else:
        return {
            "x": "",
            "y": ""
        }


def get_robot_position(robot):
    if robot is not None:
        return {
            "x": str((robot._world_position[0] * 47)),
            "y": str(-(robot._world_position[1] * 47))
        }
    else:
        return {
            "x": "",
            "y": ""
        }


def prepare_image(image):
    image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    cnt = cv2.imencode('.png', image)[1]
    image_data = base64.b64encode(cnt)
    image_data = image_data.decode('utf-8')
    return image_data


def format_message(world, robot, image):
    return {
        "headers": "push_vision_data",
        "data": {
            "image": {
                "ratio": "2.58",
                "origin": get_world_origin(world),

                "data": prepare_image(image),
                "original_dimension": {
                    "width": "1280",
                    "height": "800"
                },
                "sent_dimension": {
                    "width": "1280",
                    "height": "800"
                }
            },
            "world": {
                "unit": "cm",
                "base_table": {
                    "dimension": get_world_dimension(world)
                },
                "robot": {
                    "position": get_robot_position(robot)
                }
            },

        }
    }


if __name__ == "__main__":
    APP_ENVIRONMENT = AppEnvironment.TESTING_VISION
    WEBSOCKET = True
    VIDEO_DEBUG = not WEBSOCKET

    camera_model_repository = JSONCameraModelRepository(config.CAMERA_MODELS_FILE_PATH)
    camera_model = camera_model_repository.get_camera_model_by_id(config.TABLE_CAMERA_MODEL_ID)

    shape_factory = ShapeFactory()
    robot_detector = RobotDetector(shape_factory)
    table_detector = TableDetector(shape_factory)
    drawing_area_detector = DrawingAreaDetector(shape_factory)
    image_source = None

    if APP_ENVIRONMENT == AppEnvironment.COMPETITION:
        table_detector = DetectOnceProxy(table_detector)
        drawing_area_detector = DetectOnceProxy(drawing_area_detector)
        image_source = VideoStreamImageSource(config.CAMERA_ID)
    elif APP_ENVIRONMENT == AppEnvironment.TESTING_VISION:
        image_source = DirectoryImageSource(config.TEST_IMAGE_DIRECTORY_PATH)

    image_to_world_translator = ImageToWorldTranslator(camera_model)
    detection_service = ImageDetectionService(image_to_world_translator)

    detection_service.register_detector(robot_detector)
    detection_service.register_detector(drawing_area_detector)
    detection_service.register_detector(table_detector)

    if WEBSOCKET:
        try:
            connection = create_connection(config.BASESTATION_WEBSOCKET_URL)
            print("Connection to BaseStation established at " + config.BASESTATION_WEBSOCKET_URL + '\n')
        except ConnectionRefusedError:
            print("Could not establish connection to BaseStation url: " + config.BASESTATION_WEBSOCKET_URL)
            print("Terminating...")
            exit(0)

    while image_source.has_next_image():
        image = image_source.next_image()
        image = camera_model.undistort_image(image)
        world, robot = detection_service.translate_image_to_world(image)

        message = format_message(world, robot, image)

        if WEBSOCKET:
            try:
                connection.send(json.dumps(message))
            except NameError:
                print("No connection to websocket")

        if VIDEO_DEBUG:
            cv2.imshow("Image debug", image)
            cv2.waitKey(1)
